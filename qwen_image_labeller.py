"""
Qwen3-VL (local, via Ollama) park/playground equipment detector — test harness.
Same domain-context pattern as the Claude/Gemini versions, swapped to a local open model.

Setup:
    1. Install Ollama: https://ollama.com/download
    2. ollama pull qwen3-vl:8b   (or 4b / 30b-a3b depending on your hardware)
    3. pip install ollama pillow matplotlib pydantic

Usage:
    python qwen_park_labeller.py
"""
import os
from typing import List, Literal

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pydantic import BaseModel, Field

import ollama

MODEL = "qwen3-vl:8b-instruct"  # swap for the size that fits your hardware

PARK_CONTEXT = """You are inspecting playground/park equipment for a council asset audit.

Relevant equipment categories: slide, swing set, monkey bars, seesaw, spring rider,
climbing frame, shade structure, safety surfacing, park bench, rubbish bin, fence.

For every piece of equipment visible in the image, report its type (using the
categories above where they fit), a condition assessment of "good", "worn", or
"damaged", and its bounding box.

Only report items you can actually see. Do not guess at items that aren't visible.
Return box_2d as [x_min, y_min, x_max, y_max], normalized to 0-1000."""


class Detection(BaseModel):
    type: str
    condition: Literal["good", "worn", "damaged"]
    box_2d: List[int] = Field(description="[x_min, y_min, x_max, y_max], normalized 0-1000")


class DetectionResponse(BaseModel):
    detections: List[Detection]


CONDITION_COLORS = {"good": "green", "worn": "orange", "damaged": "red"}


def detect_park_equipment(image_path, model=MODEL):
    response = ollama.chat(
        model=model,
        format=DetectionResponse.model_json_schema(),
        messages=[{
            'role': 'user',
            'content': PARK_CONTEXT,
            'images': [image_path],
        }],
        options={'temperature': 0},
    )

    content = response['message']['content']

    if not content:
        content = response['message'].get('thinking', '')

    if not content:
        raise ValueError(f"Model returned no content or thinking output for {image_path}")

    return DetectionResponse.model_validate_json(content)


def annotate_and_save(image_path, detections, output_path):
    img = Image.open(image_path)
    width, height = img.size

    fig, ax = plt.subplots()
    ax.imshow(img)

    for det in detections.detections:
        xmin, ymin, xmax, ymax = det.box_2d
        left = xmin / 1000 * width
        top = ymin / 1000 * height
        box_width = (xmax - xmin) / 1000 * width
        box_height = (ymax - ymin) / 1000 * height

        color = CONDITION_COLORS.get(det.condition, "blue")
        rect = patches.Rectangle((left, top), box_width, box_height,
                                  linewidth=1.5, edgecolor=color, facecolor='none')
        ax.add_patch(rect)

        label_text = f"{det.type} ({det.condition})"
        ax.text(left, max(top - 2, 0), label_text, color=color, fontsize=8,
                bbox=dict(facecolor='white', alpha=0.7))

    ax.axis('off')
    fig.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close(fig)


def process_frames(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    frame_files = sorted(
        f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    )

    for i, filename in enumerate(frame_files, start=1):
        image_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        print(f"[{i}/{len(frame_files)}] Processing {filename}...")

        try:
            detections = detect_park_equipment(image_path)
            annotate_and_save(image_path, detections, output_path)
            summary = [f"{d.type} ({d.condition})" for d in detections.detections]
            print(f"  Detected: {', '.join(summary) if summary else 'nothing'}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print(f"\nDone. Annotated frames saved to {output_dir}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'extracted_frames')
    output_dir = os.path.join(script_dir, 'qwen_labeled_frames')
    process_frames(input_dir, output_dir)


if __name__ == "__main__":
    main()