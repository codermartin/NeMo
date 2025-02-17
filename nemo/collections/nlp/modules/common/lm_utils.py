# Copyright 2018 The Google AI Language Team Authors and
# The HuggingFace Inc. team.
# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from typing import List, Optional, Union

from attr import asdict

from nemo.collections.nlp.modules.common.bert_module import BertModule
from nemo.collections.nlp.modules.common.decoder_module import DecoderModule
from nemo.collections.nlp.modules.common.encoder_module import EncoderModule
from nemo.collections.nlp.modules.common.huggingface.huggingface_utils import (
    get_huggingface_lm_model,
    get_huggingface_pretrained_lm_models_list,
)
from nemo.collections.nlp.modules.common.megatron.megatron_utils import (
    get_megatron_lm_model,
    get_megatron_lm_models_list,
)
from nemo.collections.nlp.modules.common.transformer.transformer import NeMoTransformerConfig
from nemo.collections.nlp.modules.common.transformer.transformer_utils import (
    get_huggingface_transformer,
    get_megatron_transformer,
    get_nemo_transformer,
)
from nemo.utils import AppState, logging

__all__ = ['get_pretrained_lm_models_list', 'get_lm_model']


def get_pretrained_lm_models_list(include_external: bool = False) -> List[str]:
    """
    Returns the list of supported pretrained model names

    Args:
        include_external if true includes all HuggingFace model names, not only those supported language models in NeMo.

    """
    return get_megatron_lm_models_list() + get_huggingface_pretrained_lm_models_list(include_external=include_external)


def get_lm_model(
    pretrained_model_name: str,
    config_dict: Optional[dict] = None,
    config_file: Optional[str] = None,
    checkpoint_file: Optional[str] = None,
    vocab_file: Optional[str] = None,
) -> BertModule:
    """
    Helper function to instantiate a language model encoder, either from scratch or a pretrained model.
    If only pretrained_model_name are passed, a pretrained model is returned.
    If a configuration is passed, whether as a file or dictionary, the model is initialized with random weights.

    Args:
        pretrained_model_name: pretrained model name, for example, bert-base-uncased or megatron-bert-cased.
            See get_pretrained_lm_models_list() for full list.
        config_dict: path to the model configuration dictionary
        config_file: path to the model configuration file
        checkpoint_file: path to the pretrained model checkpoint
        vocab_file: path to vocab_file to be used with Megatron-LM

    Returns:
        Pretrained BertModule
    """

    # check valid model type
    if not pretrained_model_name or pretrained_model_name not in get_pretrained_lm_models_list(include_external=False):
        logging.warning(
            f'{pretrained_model_name} is not in get_pretrained_lm_models_list(include_external=False), '
            f'will be using AutoModel from HuggingFace.'
        )

    # warning when user passes both configuration dict and file
    if config_dict and config_file:
        logging.warning(
            f"Both config_dict and config_file were found, defaulting to use config_file: {config_file} will be used."
        )

    if "megatron" in pretrained_model_name:
        model, checkpoint_file = get_megatron_lm_model(
            config_dict=config_dict,
            config_file=config_file,
            pretrained_model_name=pretrained_model_name,
            checkpoint_file=checkpoint_file,
            vocab_file=vocab_file,
        )
    else:
        model = get_huggingface_lm_model(
            config_dict=config_dict, config_file=config_file, pretrained_model_name=pretrained_model_name,
        )

    if checkpoint_file:
        app_state = AppState()
        if not app_state.is_model_being_restored and not os.path.exists(checkpoint_file):
            raise ValueError(f'{checkpoint_file} not found')
        model.restore_weights(restore_path=checkpoint_file)

    return model


# @dataclass
# class TransformerConfig:
#     library: str = 'nemo'
#     model_name: Optional[str] = None
#     pretrained: bool = False
#     config_dict: Optional[dict] = None
#     checkpoint_file: Optional[str] = None
#     encoder: bool = True


def get_transformer(
    library: str = 'nemo',
    model_name: Optional[str] = None,
    pretrained: bool = False,
    config_dict: Optional[dict] = None,
    checkpoint_file: Optional[str] = None,
    encoder: bool = True,
    pre_ln_final_layer_norm=True,
) -> Union[EncoderModule, DecoderModule]:
    """Gets Transformer based model to be used as an Encoder or Decoder in NeMo NLP.
       First choose the library to get the transformer from. This can be huggingface,
       megatron, or nemo. Use the model_name arg to get a named model architecture
       and use the pretrained arg to get the named model architecture with pretrained weights.

       If model_name is None, then we can pass in a custom configuration via the config_dict.
       For example, to instantiate a HuggingFace BERT model with custom configuration we would do:
       encoder = get_transformer(library='huggingface',
                                 config_dict={
                                     '_target_': 'transformers.BertConfig',
                                     'hidden_size': 1536
                                 }) 


    Args:
        library (str, optional): Can be 'nemo', 'huggingface', or 'megatron'. Defaults to 'nemo'.
        model_name (Optional[str], optional): Named model architecture from the chosen library. Defaults to None.
        pretrained (bool, optional): Use True to get pretrained weights. 
                                     False will use the same architecture but with randomly initialized weights.
                                     Defaults to False.
        config_dict (Optional[dict], optional): Use for custom configuration of transformer. Defaults to None.
        checkpoint_file (Optional[str], optional): Provide weights for the transformer from a local checkpoint. Defaults to None.
        encoder (bool, optional): True returns an EncoderModule, False returns a DecoderModule. Defaults to True.

    Returns:
        Union[EncoderModule, DecoderModule]: Ensures that Encoder/Decoder will work in EncDecNLPModel
    """

    model = None

    if library == 'nemo':
        if isinstance(config_dict, NeMoTransformerConfig):
            config_dict = asdict(config_dict)
        model = get_nemo_transformer(
            model_name=model_name,
            pretrained=pretrained,
            config_dict=config_dict,
            encoder=encoder,
            pre_ln_final_layer_norm=pre_ln_final_layer_norm,
        )

        if checkpoint_file is not None:
            if os.path.isfile(checkpoint_file):
                raise ValueError(f'Loading transformer weights from checkpoint file has not been implemented yet.')

    elif library == 'huggingface':
        model = get_huggingface_transformer(
            model_name=model_name, pretrained=pretrained, config_dict=config_dict, encoder=encoder
        )

    elif library == 'megatron':
        model = get_megatron_transformer(
            model_name=model_name,
            pretrained=pretrained,
            config_dict=config_dict,
            encoder=encoder,
            checkpoint_file=checkpoint_file,
        )

    else:
        raise ValueError("Libary must be 'nemo', 'huggingface' or 'megatron'")

    return model
