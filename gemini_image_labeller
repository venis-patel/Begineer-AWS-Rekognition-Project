"""
Gemini-based park/playground equipment detector — test harness.

Setup:
    pip install google-genai pillow matplotlib
    export GEMINI_API_KEY="..."   # from aistudio.google.com

Usage:
    python gemini_park_labeller.py
    (reads from extracted_frames/, writes to gemini_labeled_frames/)
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()  # loads GEMINI_API_KEY from .env file if present

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Domain context — swap this block per client/field. Nothing else changes.
# ---------------------------------------------------------------------------
PARK_CONTEXT = """You are inspecting playground/park equipment for a council asset audit.

Relevant equipment categories: slide, swing set, monkey bars, seesaw, spring rider,
climbing frame, shade structure, safety surfacing, park bench, rubbish bin, fence.

For every piece of equipment visible in the image, report:
- type: the equipment category (use the categories above where they fit)
- condition: one of "good", "worn", "damaged"
- box_2d: the bounding box

Only report items you can actually see. Do not guess at items that aren't visible.
Return box_2d as [ymin, xmin, ymax, xmax], normalized to 0-1000."""


class Detection(BaseModel):
    type: str = Field(description="Equipment category")
    condition: str = Field(description='One of "good", "worn", "damaged"')
    box_2d: List[int] = Field(description="[ymin, xmin, ymax, xmax], normalized 0-1000")


class DetectionResponse(BaseModel):
    detections: List[Detection]


CONDITION_COLORS = {"good": "green", "worn": "orange", "damaged": "red"}


def detect_park_equipment(client, image_path, model="gemini-3.6-flash"):
    image = Image.open(image_path)

    response = client.models.generate_content(
        model=model,
        contents=[image, PARK_CONTEXT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DetectionResponse,
        ),
    )
    return response.parsed  # already a DetectionResponse instance


def annotate_and_save(image_path, detections, output_path):
    img = Image.open(image_path)
    width, height = img.size

    fig, ax = plt.subplots()
    ax.imshow(img)

    for det in detections.detections:
        ymin, xmin, ymax, xmax = det.box_2d
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


def process_frames(client, input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    frame_files = sorted(
        f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    )

    for i, filename in enumerate(frame_files, start=1):
        image_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"[{i}/{len(frame_files)}] Processing {filename}...")

        try:
            detections = detect_park_equipment(client, image_path)
            annotate_and_save(image_path, detections, output_path)

            summary = [f"{d.type} ({d.condition})" for d in detections.detections]
            print(f"  Detected: {', '.join(summary) if summary else 'nothing'}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print(f"\nDone. Annotated frames saved to {output_dir}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'extracted_frames')
    output_dir = os.path.join(script_dir, 'gemini_labeled_frames')

    client = genai.Client()  # reads GEMINI_API_KEY from environment

    process_frames(client, input_dir, output_dir)


if __name__ == "__main__":
    main()