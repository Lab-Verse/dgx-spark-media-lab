---
name: spark-media
description: Prepare and execute bounded local image, motion and voiceover tasks with saved receipts.
---

Read the workspace FACTS.md, PERMISSIONS.md and the repository tutorials first.
Resolve SPARK_MEDIA_REPO and SPARK_MEDIA_ROOT from the operator's local setup;
do not guess absolute paths or create another inference/orchestration service.

1. Save an original script, canonical captions, pronunciation copy and shot plan.
2. Inspect selected model/license state. Download only through the explicit
   reviewed acquisition command; an installed skill does not grant download,
   account, cloning or publication permission.
3. Check native ComfyUI queue/status and the text-model allocation. If a GPU
   handoff is needed, use only the operator's documented owned-service procedure.
   Do not invent a stop command, kill unrelated processes or enable cloud fallback.
4. Use scripts/comfy_job.py to validate the API graph before an explicit execute.
   Retain its receipt and prompt ID. On timeout observe the existing job; do not
   clear the queue, duplicate generation or assume it failed.
5. For public speech examples use scripts/voiceover.py in the qualified runtime.
   Keep generated speech/raw takes private until their use is approved. Never
   access or upload another profile's voice reference or embedding.
6. Use scripts/verify_media.py for technical checks, then require visual/native
   listening review. A codec diagnostic is not AI generation; ASR is not listening.
7. Record native and delivery dimensions/fps, selected source ranges, hashes,
   timing and failures. Restore the original text route and prove inference.
8. Save local drafts. Publishing, sending, account actions, payments and deployment
   require the operator's explicit destination/action authorization.

Profiles share an OS user and are not a security sandbox. All downloaded models
are not automatically runtime tested. Report blocked and unknown outcomes plainly.
