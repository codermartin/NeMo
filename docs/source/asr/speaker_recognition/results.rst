Checkpoints
===========

There are two main ways to load pretrained checkpoints in NeMo:

* Using the :code:`restore_from()` method to load a local checkpoint file (`.nemo`), or
* Using the :code:`from_pretrained()` method to download and set up a checkpoint from NGC.

See the following sections for instructions and examples for each.

Note that these instructions are for loading fully trained checkpoints for evaluation or fine-tuning.
For resuming an unfinished training experiment, please use the experiment manager to do so by setting the
``resume_if_exists`` flag to True.

Loading Local Checkpoints
-------------------------

NeMo will automatically save checkpoints of a model you are training in a `.nemo` format.
You can also manually save your models at any point using :code:`model.save_to(<checkpoint_path>.nemo)`.

If you have a local ``.nemo`` checkpoint that you'd like to load, simply use the :code:`restore_from()` method:

.. code-block:: python

  import nemo.collections.asr as nemo_asr
  model = nemo_asr.models.<MODEL_BASE_CLASS>.restore_from(restore_path="<path/to/checkpoint/file.nemo>")

Where the model base class is the ASR model class of the original checkpoint, or the general `ASRModel` class.

Speaker Label Inference
------------------------

Speaker label Inference, is to infer speaker labels from a pretrained speaker model with known speaker labels. We provide `speaker_reco_infer.py` script for this purpose under `<NeMo_root>/examples/speaker_tasks/recognition` folder.

The audio files should be 16KHz monochannel wav files.

Write audio files to a ``manifest.json`` file with lines as in format:

.. code-block:: json
    
    {"audio_filepath": "<absolute path to dataset>/audio_file.wav", "duration": "duration of file in sec", "label": "UNK"}
      
This python call will use the pretrain model and infer labels on provided test set using labels from trained manifest file

.. code-block:: bash
  
    python speaker_reco_infer.py --spkr_model='/path/to/.nemo/file' --train_manifest='/path/to/train/manifest/file'
    --test_manifest=/path/to/train/manifest/file' --batch_size=32
    
Speaker Embedding Extraction
-----------------------------
Speaker Embedding Extraction, is to extract speaker embeddings for any wav file (from known or unkown speakers). We provide two ways to do this:

* single python liner for extracting embeddings from a single file 
* python script for extracting embeddings from a bunch of files provided through manifest file

For extracting embeddings from a single file:

.. code-block:: python

  speaker_model = EncDecSpeakerLabelModel.from_pretrained(model_name="<pretrained_model_name or path/to/nemo/file>")
  embs = speaker_model.get_embedding('audio_path')

For extracting embeddings from a bunch of files:

The audio files should be 16KHz monochannel wav files.

Write audio files to a ``manifest.json`` file with lines as in format:

.. code-block:: json
    
    {"audio_filepath": "<absolute path to dataset>/audio_file.wav", "duration": "duration of file in sec", "label": "speaker_id"}
      
This python call will download best pretrained model from NGC and writes embeddings pickle file to current working directory

.. code-block:: bash
  
    python examples/speaker_tasks/recognition/extract_speaker_embeddings.py --manifest=manifest.json


NGC Pretrained Checkpoints
--------------------------

The SpeakerNet-ASR collection has checkpoints of several models trained on various datasets for a variety of tasks.
`Speaker_Recognition <https://ngc.nvidia.com/catalog/models/nvidia:nemo:speakerrecognition_speakernet>`_ and `Speaker_Verification <https://ngc.nvidia.com/catalog/models/nvidia:nemo:speakerverification_speakernet>`_ model cards on NGC contain more information about each of the checkpoints available.

The tables below list the SpeakerNet models available from NGC, and the models can be accessed via the
:code:`from_pretrained()` method inside the EncDecSpeakerLabelModel Model class.

.. note:: While loading, remember to use EncDecSpeakerLabelModel for recognition tasks and ExtractSpeakerEmbeddingsModel while extracting embeddings.

In general, you can load any of these models with code in the following format.

.. code-block:: python

  import nemo.collections.asr as nemo_asr
  model = nemo_asr.models.<MODEL_CLASS_NAME>.from_pretrained(model_name="<MODEL_NAME>")

Where the model name is the value under "Model Name" entry in the tables below.

If you would like to programatically list the models available for a particular base class, you can use the
:code:`list_available_models()` method.

.. code-block:: python

  nemo_asr.models.<MODEL_BASE_CLASS>.list_available_models()


Speaker Recognition Models
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :file: data/speaker_results.csv
   :align: left
   :widths: 30, 30, 40
   :header-rows: 1

