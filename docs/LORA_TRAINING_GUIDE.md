# Character LoRA Training Guide

Complete guide for training character LoRAs to generate consistent friend representations in Quentin Blake style illustrations.

## Quick Reference

**Hardware**: 14" M1 Max (64GB RAM) using MPS (Metal)  
**Trigger Format**: `qb_[name]` (e.g., `qb_peter`, `qb_maria`)  
**Training Time**: ~45-60 min for 1200 steps  
**Images Needed**: 20-40 per person  

## Prerequisites

### One-Time Setup
```bash
# Create training environment
/usr/bin/python3 -m venv ~/sd-train-venv
~/sd-train-venv/bin/pip install --upgrade pip

# Clone kohya sd-scripts
git clone https://github.com/kohya-ss/sd-scripts ~/sd-scripts

# Install dependencies (pinned versions to avoid conflicts)
~/sd-train-venv/bin/pip install torch torchvision torchaudio
~/sd-train-venv/bin/pip install accelerate safetensors einops peft sentencepiece opencv-python albumentations datasets
~/sd-train-venv/bin/pip install diffusers==0.25.0 transformers==4.44.0 huggingface_hub==0.24.5

# Configure accelerate
~/sd-train-venv/bin/accelerate config default

# Verify MPS is available
~/sd-train-venv/bin/python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

### Required Paths
- Base model: `/Users/peter_coulson/stable-diffusion-webui/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors`
- Output LoRAs: `/Users/peter_coulson/stable-diffusion-webui/models/Lora/`
- Datasets: `/Users/peter_coulson/datasets/friends/[name]/`

## Training Process

### Step 1: Prepare Dataset

Create folder structure with repeats prefix (controls training epochs):
```bash
FRIEND=peter  # Change for each friend
mkdir -p "/Users/peter_coulson/datasets/friends/$FRIEND/30_${FRIEND}"
```

Add 20-40 images:
- Various angles (front, 3/4, profile)
- Different expressions and lighting
- Clear face visibility (no sunglasses/heavy shadows)
- Mix of contexts/backgrounds

### Step 2: Preprocess Images

Normalize to 512×512 with letterboxing (prevents training errors):
```bash
brew list imagemagick >/dev/null 2>&1 || brew install imagemagick

FRIEND=peter  # Change for each friend
IMG_DIR="/Users/peter_coulson/datasets/friends/$FRIEND/30_${FRIEND}"

# Convert all images to JPG
magick mogrify -format jpg "$IMG_DIR"/*.{png,PNG,jpeg,JPEG,jpg,JPG} 2>/dev/null || true

# Resize and letterbox to 512×512
magick mogrify -strip -resize x512\> -background white -gravity center -extent 512x512 -format jpg "$IMG_DIR"/*.jpg

# Verify all are 512×512
identify -format "%w x %h %f\n" "$IMG_DIR"/*.jpg | sort | uniq
```

### Step 3: Create Captions

Generate caption files (same basename as images):
```bash
FRIEND=peter  # Change for each friend
TOKEN=qb_peter  # Change for each friend
BASE="/Users/peter_coulson/datasets/friends/$FRIEND/30_${FRIEND}"

# Create basic caption files
for f in "$BASE"/*.jpg; do
  [ -e "$f" ] || continue
  basename="${f%.*}"
  echo "$TOKEN person, describe appearance here" > "${basename}.txt"
done
```

Edit each `.txt` file to include:
- Trigger token (e.g., `qb_peter`)
- Key features (hair color/style, glasses, typical expression)
- Avoid over-specific clothing/backgrounds

Example caption:
```
qb_peter person, man, curly hair, glasses, friendly smile
```

### Step 4: Train LoRA

**Standard Training** (stable, ~60 min):
```bash
FRIEND=peter  # Change for each friend
TOKEN=qb_peter  # Change for each friend

PYTORCH_ENABLE_MPS_FALLBACK=1 \
~/sd-train-venv/bin/accelerate launch ~/sd-scripts/train_network.py \
  --pretrained_model_name_or_path \
  "/Users/peter_coulson/stable-diffusion-webui/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors" \
  --train_data_dir "/Users/peter_coulson/datasets/friends/$FRIEND" \
  --caption_extension ".txt" \
  --resolution 512,512 \
  --output_dir "/Users/peter_coulson/stable-diffusion-webui/models/Lora" \
  --logging_dir "/Users/peter_coulson/datasets/logs/$FRIEND" \
  --network_module networks.lora \
  --network_dim 16 --network_alpha 8 \
  --learning_rate 1e-4 --text_encoder_lr 5e-5 \
  --optimizer_type AdamW --lr_scheduler cosine \
  --max_train_steps 1200 \
  --train_batch_size 1 \
  --gradient_checkpointing \
  --mixed_precision no \
  --save_every_n_steps 400 \
  --save_model_as safetensors \
  --output_name "${TOKEN}_lora"
```

**Fast Training** (1.5-1.8× faster, ~35-40 min):
```bash
FRIEND=peter  # Change for each friend
TOKEN=qb_peter  # Change for each friend

PYTORCH_ENABLE_MPS_FALLBACK=1 \
~/sd-train-venv/bin/accelerate launch ~/sd-scripts/train_network.py \
  --pretrained_model_name_or_path \
  "/Users/peter_coulson/stable-diffusion-webui/models/Stable-diffusion/v1-5-pruned-emaonly.safetensors" \
  --train_data_dir "/Users/peter_coulson/datasets/friends/$FRIEND" \
  --caption_extension ".txt" \
  --resolution 512,512 \
  --output_dir "/Users/peter_coulson/stable-diffusion-webui/models/Lora" \
  --logging_dir "/Users/peter_coulson/datasets/logs/$FRIEND" \
  --network_module networks.lora \
  --network_dim 16 --network_alpha 8 \
  --learning_rate 1e-4 --text_encoder_lr 5e-5 \
  --optimizer_type AdamW --lr_scheduler cosine \
  --max_train_steps 1200 \
  --train_batch_size 1 \
  --mixed_precision fp16 \
  --save_every_n_steps 400 \
  --save_model_as safetensors \
  --output_name "${TOKEN}_lora" \
  --cache_latents \
  --persistent_data_loader_workers \
  --dataloader_num_workers 4 \
  --network_train_unet_only
```

### Step 5: Test in Automatic1111

Use in prompts:
```
<lora:qb_peter_lora:0.8>, qb_peter person climbing tree, illustration in the style of Quentin Blake, watercolor, whimsical
```

Adjust weight (0.6-1.0) for stronger/weaker likeness.

## Quality Improvements

For better results:
- Increase `--max_train_steps` to 3000-6000
- Increase `--network_dim` to 32 (with `--network_alpha 16`)
- Add more varied images (aim for 40-50)
- Refine captions with consistent descriptors

## Trained Characters Registry

Track completed LoRAs here:

| Name | Token | Date Trained | Steps | Images | Notes |
|------|-------|--------------|-------|--------|-------|
| Peter | qb_peter | 2025-08-10 | 1200 | 35 | Initial training |
| | | | | | |

## Integration with Fluent Forever System

The automation.py script automatically includes LoRA tokens in prompts:
1. User writes: "Peter climbing a tree"
2. System converts to: "<lora:qb_peter_lora:0.8>, qb_peter person climbing tree, Quentin Blake style..."
3. Generates consistent character representation

## Troubleshooting

**Training won't start**: Ensure all images are 512×512 (use preprocessing step)

**NaN errors**: Switch from `--mixed_precision fp16` to `--mixed_precision no`

**Out of memory**: Keep `--train_batch_size 1` and `--resolution 512,512`

**Results don't look like person**: 
- Add more front-facing images
- Make captions more consistent
- Train for more steps (2000-3000)

**Check training status**:
```bash
ps aux | grep train_network.py | grep -v grep
```

**Stop training**:
```bash
pkill -f train_network.py
```

## Next Friend Checklist

- [ ] Create dataset folder: `/Users/peter_coulson/datasets/friends/[name]/30_[name]/`
- [ ] Add 20-40 photos
- [ ] Preprocess to 512×512
- [ ] Create caption files with trigger token
- [ ] Run training (45-60 min)
- [ ] Test in Automatic1111
- [ ] Update registry table above
- [ ] Add to config.json if needed

---

*Last updated: August 10, 2025*
