import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import models
import comfy_job
import check_llm
import make_score
import verify_media
import voiceover


class PathsAndIntegrity(unittest.TestCase):
    def test_manifest_safety_and_verification_metadata(self):
        manifest = json.loads(models.MANIFEST.read_text())
        destinations = set()
        for item in manifest['files']:
            self.assertNotIn(item['destination'], destinations)
            destinations.add(item['destination'])
            models.target(ROOT, item['destination'])
            self.assertTrue(models.url_for(item).startswith('https://'))
            self.assertGreater(item['size_bytes'], 0)
            self.assertTrue(item.get('sha256') or item.get('git_blob_sha1'))
            if 'revision' in item:
                self.assertRegex(item['revision'], r'^[a-f0-9]{40}$')

    def test_destination_traversal_and_absolute_paths_rejected(self):
        for path in ['../escape', '/tmp/escape', 'C:/escape', 'x\\..\\escape']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                models.target(ROOT, path)

    def test_corrupt_existing_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'file'
            path.write_bytes(b'abc')
            item = {'destination': 'file', 'size_bytes': 3, 'sha256': hashlib.sha256(b'abc').hexdigest(), 'verification': 'test'}
            self.assertEqual(models.verify(path, item)['bytes'], 3)
            path.write_bytes(b'bad')
            with self.assertRaises(ValueError):
                models.verify(path, item)

    def test_git_object_hash_includes_blob_header(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'f'
            path.write_bytes(b'hello')
            self.assertEqual(models.digest(path, True), hashlib.sha1(b'blob 5\0hello').hexdigest())

    def test_voice_output_must_be_new_child_of_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(voiceover.output_path(root, root/'runs/take-1'), (root/'runs/take-1').resolve())
            for output in [root/'runs/../../escape', root/'other', root/'runs']:
                with self.assertRaises(ValueError):
                    voiceover.output_path(root, output)

    def test_non_loopback_and_redirects_rejected(self):
        for url in ['https://example.com', 'http://127.0.0.1.evil.test', 'http://user@localhost', 'http://localhost?key=x']:
            with self.assertRaises(ValueError):
                check_llm.local_url(url)
        with self.assertRaises(ValueError):
            check_llm.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.com')


class WorkflowBehavior(unittest.TestCase):
    def test_all_api_graphs_are_acyclic_and_links_resolve(self):
        for path in (ROOT/'workflows/api').glob('*.json'):
            comfy_job.validate_graph(json.loads(path.read_text()))

    def test_invalid_graph_links_and_cycles_rejected(self):
        for graph in [{'1': {'class_type': 'X', 'inputs': {'x': ['99', 0]}}},
                      {'1': {'class_type': 'X', 'inputs': {'x': ['1', 0]}}}]:
            with self.assertRaises(ValueError):
                comfy_job.validate_graph(graph)

    def test_schema_model_choice_checked(self):
        graph = {'1': {'class_type': 'Loader', 'inputs': {'model': 'missing'}}}
        info = {'Loader': {'input': {'required': {'model': [['present']]}}, 'output': []}}
        with self.assertRaises(ValueError):
            comfy_job.validate_graph(graph, info)

    def test_success_observation_preserves_native_history(self):
        result = {'job': {'status': {'status_str': 'success', 'completed': True}, 'outputs': {'1': {}}}}
        with tempfile.TemporaryDirectory() as temp, patch.object(comfy_job, 'call', return_value=result), contextlib.redirect_stdout(io.StringIO()):
            path = Path(temp)/'receipt.json'
            comfy_job.observe('http://localhost:8188', 'job', path, {}, 1)
            self.assertEqual(json.loads(path.read_text())['state'], 'completed')

    def test_timeout_never_submits_or_cancels(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(comfy_job, 'call') as call:
            path = Path(temp)/'receipt.json'
            with self.assertRaises(SystemExit):
                comfy_job.observe('http://localhost', 'job', path, {'prompt_id': 'job'}, 0)
            call.assert_not_called()
            self.assertEqual(json.loads(path.read_text())['state'], 'outcome_unknown')

    def test_connection_loss_preserves_unknown_outcome(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(comfy_job, 'call', side_effect=OSError('offline')):
            path = Path(temp)/'receipt.json'
            with self.assertRaises(OSError):
                comfy_job.observe('http://localhost', 'job', path, {'prompt_id': 'job'}, 1)
            self.assertEqual(json.loads(path.read_text())['state'], 'outcome_unknown')

    def test_lost_post_response_exposes_receipt_and_never_retries(self):
        graph = {'1': {'class_type': 'X', 'inputs': {}}}
        info = {'X': {'input': {'required': {}}, 'output': []}}
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            source = directory/'graph.json'
            source.write_text(json.dumps(graph))
            stream = io.StringIO()
            replies = [info, {'queue_running': [], 'queue_pending': []}, OSError('lost response')]
            with patch.object(sys, 'argv', ['comfy_job.py', 'submit', str(source), '--receipts', str(directory/'receipts'), '--execute']), \
                 patch.object(comfy_job, 'call', side_effect=replies) as call, contextlib.redirect_stdout(stream):
                with self.assertRaises(OSError):
                    comfy_job.main()
            self.assertEqual(sum(c.args[1] == '/prompt' for c in call.call_args_list), 1)
            message = json.loads(stream.getvalue())
            receipt = json.loads(Path(message['receipt']).read_text())
            self.assertEqual(receipt['client_id'], message['client_id'])
            self.assertEqual(receipt['state'], 'submission_outcome_unknown')


class AudioBehavior(unittest.TestCase):
    def test_codec_mismatch_fails_closed(self):
        voiceover.codec_keys(['ssl_feature_extractor.a', 'conv_upsample.b', 'istft_head.istft.window'], [])
        for missing, unexpected in [(['decoder.weight'], []), ([], ['unexpected'])]:
            with self.assertRaises(ValueError):
                voiceover.codec_keys(missing, unexpected)

    def test_speech_token_extraction(self):
        self.assertEqual(voiceover.speech_codes([1, 100, 102, 13000], 100), [0, 2])
        with self.assertRaises(ValueError):
            voiceover.speech_codes([1, 2], 100)

    def test_plain_narration_ids_and_control_tags(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'script.json'
            for data in [[{'id': '../escape', 'text': 'hello'}], [{'id': 'x', 'text': '<control>'}], [42]]:
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    voiceover.segments_from(path)
            self.assertEqual(len(voiceover.segments_from(ROOT/'examples/narration.json')), 1)

    def test_procedural_score_duration_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'score.wav'
            make_score.write_score(path, .5)
            with wave.open(str(path)) as audio:
                self.assertEqual(audio.getnframes(), 12000)
                self.assertEqual(audio.getframerate(), 24000)
                self.assertTrue(any(audio.readframes(12000)))
            with self.assertRaises(FileExistsError):
                make_score.write_score(path, .5)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg tools unavailable')
    def test_real_ffmpeg_decode_and_required_streams(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'score.wav'
            make_score.write_score(path, .5)
            self.assertEqual(verify_media.verify(path, audio=True)['full_decode'], 'PASS')
            with self.assertRaises(ValueError):
                verify_media.verify(path, video=True)


if __name__ == '__main__':
    unittest.main()
