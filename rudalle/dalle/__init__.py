# -*- coding: utf-8 -*-
import os

import torch
from huggingface_hub import hf_hub_url, cached_download

from .model import DalleModel
from .fp16 import FP16Module


MODELS = {
    'Malevich': dict(
        description='◼️ Malevich is 1.3 billion params model from the family GPT3-like, '
                    'that uses Russian language and text+image multi-modality.',
        model_params=dict(
            num_layers=24,
            hidden_size=2048,
            num_attention_heads=16,
            embedding_dropout_prob=0.1,
            output_dropout_prob=0.1,
            attention_dropout_prob=0.1,
            image_tokens_per_dim=32,
            text_seq_length=128,
            use_masks=True,
            cogview_sandwich_layernorm=True,
            cogview_pb_relax=True,
            vocab_size=16384+128,
            image_vocab_size=8192*2,
            # image_vocab_size=8192,
        ),
        # repo_id='sberbank-ai/rudalle-Malevich',  # TODO update checkpoint
        repo_id='shonenkov/rudalle-Malevich',
        filename='pytorch_model.bin',
        full_description='',  # TODO
    ),
    'small': dict(
        description='',
        model_params=dict(
            num_layers=12,
            hidden_size=768,
            num_attention_heads=12,
            embedding_dropout_prob=0.1,
            output_dropout_prob=0.1,
            attention_dropout_prob=0.1,
            image_tokens_per_dim=32,
            text_seq_length=128,
            use_masks=True,
            cogview_sandwich_layernorm=True,
            cogview_pb_relax=True,
            vocab_size=16384+128,
            image_vocab_size=8192,
        ),
        repo_id='',
        filename='',
        full_description='',  # TODO
    ),
}


def get_rudalle_model(name, pretrained=True, fp16=False, device='cpu', cache_dir='/tmp/rudalle'):
    # TODO docstring
    assert name in MODELS

    config = MODELS[name]
    model = DalleModel(device=device, fp16=fp16, **config['model_params'])
    if pretrained:
        cache_dir = os.path.join(cache_dir, name)
        config_file_url = hf_hub_url(repo_id=config['repo_id'], filename=config['filename'])
        cached_download(config_file_url, cache_dir=cache_dir, force_filename=config['filename'])
        checkpoint = torch.load(os.path.join(cache_dir, config['filename']), map_location='cpu')
        if 'module' in checkpoint:
            checkpoint = checkpoint['module']
        model.load_state_dict(checkpoint, strict=False)
    if fp16:
        model = FP16Module(model)
    model.eval()
    model = model.to(device)
    if config['description'] and pretrained:
        print(config['description'])
    return model
