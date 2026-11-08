# Three launch-post drafts

Prepared for Labverse. These are editable publication drafts; no social post is sent by this repository.

## Post 1 — The open-source contribution

We are sharing our DGX Spark media research as a public Labverse repository.

The guide covers the route from a local agent to an original video: Hermes, a local text endpoint, ComfyUI image/video workflows, experimental Urdu narration, audio finishing and practical verification.

It includes three tutorials, pinned model selections, workflow files and small tools that save native job IDs and receipts. We also documented what failed and what still needs testing.

One lesson shaped the whole setup: owning a 128 GB Spark does not mean every model should run together. Our text service reserved roughly 99 GiB, so heavy video generation needed a deliberate GPU handoff and a verified return to text inference.

The original research produced short motion/voice samples and a 147-second full-motion Urdu experiment. The exported public setup still needs clean-machine qualification; it is a community starting point with explicit limits.

If you work with Spark, ARM64 media runtimes or Urdu speech, contributions with measured results would be especially useful.

Repository: https://github.com/Lab-Verse/dgx-spark-media-lab

#DGXSpark #OpenSource #ComfyUI #HermesAgent #Labverse

## Post 2 — Video tutorial

A generated MP4 is only the beginning of a video workflow.

During our DGX Spark experiments, an early 147-second montage passed technical checks but did not meet the creative brief: too much of its visual track was animated still images. The replacement used 30 locally generated Wan clips and a ledger connecting the edit to source frames.

We have turned those lessons into a practical tutorial:

- Generate one image and one short moving clip before scaling up.
- Keep UI workflows separate from execution graphs.
- Save prompts, model revisions, seeds and native prompt IDs.
- Measure the first render rather than guessing throughput.
- Inspect motion at full speed; unique frames cannot prove convincing acting or correct physics.
- Resume observation after a timeout instead of submitting duplicate jobs.

Our public starter includes Wan T2V/I2V graphs and a clearly labeled export-only diagnostic. It distinguishes historical runtime evidence from the new public recipe.

Read the tutorial: https://github.com/Lab-Verse/dgx-spark-media-lab/blob/main/tutorials/02-images-and-video.md

#AIVideo #WanVideo #DGXSpark #ComfyUI #BuildInPublic

## Post 3 — Voice and audio tutorial

Urdu voiceover taught us to separate three questions: did the audio decode, did it say the intended words, and did it sound right to a listener?

A speech recognizer can help flag missing words. It cannot settle every nasal vowel, name pronunciation or change in perceived speaker identity.

Our new Labverse tutorial covers short local Indic-Mio auditions, the exact MioCodec/WavLM dependency chain, sampling controls, modest pace changes, narration/music mixing and caption review.

It also makes the privacy boundary explicit: our private consented voice reference and embeddings are excluded. The public code uses an experimental synthetic baseline, so contributors can study the setup without receiving anyone's voice identity.

The audio example includes a simple original procedural score. We have acquired neural music models in the broader research, but we are not presenting their downloads as successful music-generation benchmarks.

If you contribute a speech result, include the language/script, model revisions, settings, timing and native-listener feedback. That evidence is more useful than a blanket “multilingual works” claim.

Read the tutorial: https://github.com/Lab-Verse/dgx-spark-media-lab/blob/main/tutorials/03-voice-audio-and-finishing.md

#UrduAI #TextToSpeech #LocalAI #OpenSource #Labverse
