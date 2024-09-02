import csv
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime

def get_panorama_path():
    return "resources/panoramas/Panorama_Background_S.png"  # Hardcoded until more are exported from the game

def get_logo_path():
    return "resources/mc-lce-decomp-logo.png"

def get_font_path():
    return "resources/Minecraft-Seven.otf"

def read_progress_data(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            version = int(row[0])
            timestamp = int(row[1])
            git_hash = row[2]
            num_total = int(row[3])
            code_size_total = int(row[4])
            matching_count = int(row[5])
            matching_code_size = int(row[6])
            equivalent_count = int(row[7])
            equivalent_code_size = int(row[8])
            non_matching_count = int(row[9])
            non_matching_code_size = int(row[10])
            
            return {
                "version": version,
                "timestamp": timestamp,
                "git_hash": git_hash,
                "num_total": num_total,
                "code_size_total": code_size_total,
                "matching_count": matching_count,
                "matching_code_size": matching_code_size,
                "equivalent_count": equivalent_count,
                "equivalent_code_size": equivalent_code_size,
                "non_matching_count": non_matching_count,
                "non_matching_code_size": non_matching_code_size,
            }

def draw_background(total_width, total_height):
    background = Image.open(get_panorama_path())
    orig_width, orig_height = background.size

    original_aspect = orig_width / orig_height
    desired_aspect = total_width / total_height

    if original_aspect > desired_aspect:
        new_height = total_height
        new_width = int(orig_width * (new_height / orig_height))
    else:
        new_width = total_width
        new_height = int(orig_height * (new_width / orig_width))

    background = background.resize((new_width, new_height))

    left = (new_width - total_width) / 2
    top = (new_height - total_height) / 2
    right = (new_width + total_width) / 2
    bottom = (new_height + total_height) / 2

    background = background.crop((left, top, right, bottom))
    background = background.filter(ImageFilter.GaussianBlur(radius=5))

    return background

def draw_logo(total_width, total_height):
    logo = Image.open(get_logo_path()).convert("RGBA")
    logo_width, logo_height = logo.size

    size = 600

    logo = logo.resize((size, int(size * logo_height/logo_width)), Image.LANCZOS)

    logo_x = (total_width - size) // 2
    logo_y = 30
    return logo, logo_x, logo_y

def create_progress_bar(progress_percentage, matching_count, major_mismatch_count, minor_mismatch_count, total_count, decompiled_size, code_size_total):
    padding_x=60
    logo_padding = 150
    padding_y=30

    width = 750
    height = 300

    total_width = width + 2 * padding_x
    total_height = height + 2 * padding_y

    background = draw_background(total_width, total_height)

    image = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    logo, logo_x, logo_y = draw_logo(total_width, total_height)
    image.paste(logo, (logo_x, logo_y), logo)

    rect_x0 = padding_x + 50
    rect_y0 = padding_y + logo_padding
    rect_x1 = total_width - padding_x - 50
    rect_y1 = int(height * .13) + padding_y + logo_padding

    # Inner progress bar fill
    draw.rectangle(
        [rect_x0, rect_y0, rect_x1, rect_y1],
        fill=(162, 162, 162, 255)
    )

    # Outer progress bar fill
    draw.rectangle(
        [rect_x0, rect_y0, rect_x1, rect_y1],
        outline=(100, 100, 100, 255),
        width=3
    )

    # Calculate the fill widths
    if total_count > 0:
        matching_fill_width = (matching_count / total_count) * (width - 20)
        major_mismatch_fill_width = (major_mismatch_count / total_count) * (width - 20)
        minor_mismatch_fill_width = (minor_mismatch_count / total_count) * (width - 20)
    else:
        matching_fill_width = major_mismatch_fill_width = minor_mismatch_fill_width = 0

    # Draw progress fills
    draw.rectangle(
        [rect_x0 + 5, rect_y0 + 5,
         rect_x0 + 5 + matching_fill_width, rect_y1 - 5],
        fill=(38, 213, 34, 255)  # Green
    )
    
    draw.rectangle(
        [rect_x0 + 5 + matching_fill_width, rect_y0 + 5,
         rect_x0 + 5 + matching_fill_width + major_mismatch_fill_width, rect_y1 - 5],
        fill=(240, 120, 120, 255)  # Orange
    )

    # Draw the percentage text
    percentage_text = f"{progress_percentage:.3f}% | {matching_count + major_mismatch_count + minor_mismatch_count}/{total_count} functions"
    font = ImageFont.truetype(get_font_path(), 20)
    text_bbox = draw.textbbox((0, 0), percentage_text, font=font)
    text_x = (total_width - (text_bbox[2] - text_bbox[0])) // 2
    text_y = (rect_y0 + rect_y1) // 2 - (text_bbox[3] - text_bbox[1]) // 2
    draw.text((text_x + 1, text_y + 1), percentage_text, fill="black", stroke_width=1, stroke_fill='black', font=font)
    draw.text((text_x, text_y), percentage_text, fill="white", stroke_width=1, stroke_fill='black', font=font)

    # Draw the text area below the progress bar
    text_area_y0 = rect_y1 + 15
    text_area_y1 = total_height - padding_y

    # Inner tooltip fill
    draw.rounded_rectangle(
        [padding_x, text_area_y0, total_width - padding_x, text_area_y1],
        fill=(85, 110, 110, 225),
        radius=3
    )

    # Outer tooltip fill
    draw.rounded_rectangle(
        [padding_x, text_area_y0, total_width - padding_x, text_area_y1],
        outline=(255, 255, 255, 255),
        width=int(2),
        radius=3
    )

    details_text = (f"{datetime.today().strftime('%m/%d/%Y')} | "
                    f"{matching_count} matched, {major_mismatch_count + minor_mismatch_count} mismatched functions | {decompiled_size}/{code_size_total} kB")
    
    font = ImageFont.truetype(get_font_path(), 20)

    detail_text_bbox = draw.textbbox((0, 0), details_text, font=font)
    detail_text_x = (total_width - (detail_text_bbox[2] - detail_text_bbox[0])) // 2
    detail_text_y = text_area_y0 + (text_area_y1 - text_area_y0) // 2 - (detail_text_bbox[3] - detail_text_bbox[1]) // 2
    draw.text((detail_text_x, detail_text_y), details_text, fill="white", stroke_width=1, stroke_fill="black", font=font)

    # Save the image
    image = image.resize((total_width, total_height))
    image = Image.alpha_composite(background, image)
    image.save("img/progress.png", format="PNG")

def main():
    progress_data = read_progress_data('progress.csv')
    
    total_count = progress_data['num_total'] if progress_data['num_total'] > 0 else 1

    matching_count = progress_data['matching_count']
    minor_mismatch_count = progress_data['equivalent_count']
    major_mismatch_count = progress_data['non_matching_count']

    decompiled_size = round((progress_data['matching_code_size'] + progress_data['equivalent_code_size'] + progress_data['non_matching_code_size']) / 1000, 2)  # Assuming non_matching_count as minor mismatch
    code_size_total = int(progress_data['code_size_total'] / 1000)
    
    progress_percentage = (matching_count / total_count) * 100
    rounded_percentage = round(progress_percentage, 3)

    create_progress_bar(rounded_percentage, matching_count, major_mismatch_count, minor_mismatch_count, total_count, decompiled_size, code_size_total)

    print("Progress image generated and saved as 'img/progress.png'.")

if __name__ == "__main__":
    main()
