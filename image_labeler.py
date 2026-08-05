import boto3
import os
import matplotlib
matplotlib.use('Agg')  # non-interactive backend — required for saving in a loop without blocking
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image


def detect_labels_local(client, image_path, max_labels=10, min_confidence=70):
    with open(image_path, 'rb') as img_file:
        image_bytes = img_file.read()

    response = client.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=max_labels,
        MinConfidence=min_confidence
    )
    return response


def annotate_and_save(image_path, response, output_path):
    img = Image.open(image_path)

    fig, ax = plt.subplots()
    ax.imshow(img)

    for label in response['Labels']:
        for instance in label.get('Instances', []):
            bbox = instance['BoundingBox']
            left = bbox['Left'] * img.width
            top = bbox['Top'] * img.height
            width = bbox['Width'] * img.width
            height = bbox['Height'] * img.height

            rect = patches.Rectangle((left, top), width, height,
                                      linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

            label_text = f"{label['Name']} ({round(label['Confidence'], 1)}%)"
            ax.text(left, max(top - 2, 0), label_text, color='r', fontsize=8,
                    bbox=dict(facecolor='white', alpha=0.7))

    # labels with no bounding box (scene-level, e.g. "Indoors", "Lighting")
    scene_labels = [l['Name'] for l in response['Labels'] if not l.get('Instances')]
    if scene_labels:
        ax.text(5, 15, "Scene: " + ", ".join(scene_labels[:5]),
                color='blue', fontsize=7, bbox=dict(facecolor='white', alpha=0.7))

    ax.axis('off')
    fig.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close(fig)  # frees memory — important when processing many frames in a loop


def process_frames(input_dir, output_dir, min_confidence=70):
    os.makedirs(output_dir, exist_ok=True)
    client = boto3.client('rekognition')

    frame_files = sorted(
        f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    )

    for i, filename in enumerate(frame_files, start=1):
        image_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"[{i}/{len(frame_files)}] Processing {filename}...")

        try:
            response = detect_labels_local(client, image_path, min_confidence=min_confidence)
            annotate_and_save(image_path, response, output_path)

            label_names = [l['Name'] for l in response['Labels']]
            print(f"  Labels: {', '.join(label_names) if label_names else 'none'}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print(f"\nDone. Annotated frames saved to {output_dir}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, 'extracted_frames')
    output_dir = os.path.join(script_dir, 'labeled_frames')
    process_frames(input_dir, output_dir)


if __name__ == "__main__":
    main()