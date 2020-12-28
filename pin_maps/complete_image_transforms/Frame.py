# Internal modules
from complete_image_transforms.CompleteImageTransform import CompleteImageTransform
# External modules
from PIL import Image, ImageDraw

class Frame(CompleteImageTransform):
    """Frames the image."""

    def __init__(self, added_frame_px: int, border_wanted: bool, border_thickness: int = 3):
        """
        Args:
            added_frame_px (int): The number if pixels added as frame.
            border_wanted (bool): Whether a border should be inserted into the new frame.
            border_thickness (int, optional): Number of pixels of the border. Defaults to 3.
        """
        super().__init__()
        self.added_frame_px = added_frame_px
        self.border_wanted = border_wanted
        self.border_thickness = border_thickness


    def transform(self, img: Image.Image) -> Image.Image:
        orig_width, orig_height = img.size
        new_frame_height = orig_height + self.added_frame_px
        new_frame_width = (12 / 18) * (orig_height + self.added_frame_px)
        if new_frame_width < orig_width:
            raise ValueError(f'Neue Breite ist kleiner als alte {new_frame_width} zu {orig_width}.')
            
        frame_dims = (round(new_frame_width), round(new_frame_height))
        framed_img = Image.new(img.mode, frame_dims, (255, ) * 3)

        addtional_width = round(new_frame_width - orig_width)
        pasting_pos = (round(addtional_width / 2), round(self.added_frame_px / 2))
        framed_img.paste(img, pasting_pos)

        if self.border_wanted:
            half_frame_px = round(self.added_frame_px / 2) # Halbe Breite des Rands
            upper_left_corner = (half_frame_px, ) * 2
            upper_right_corner = (new_frame_width - half_frame_px, half_frame_px)
            lower_left_corner = (half_frame_px, new_frame_height - half_frame_px)
            lower_right_corner = (new_frame_width - half_frame_px, new_frame_height - half_frame_px)
            shape = [upper_left_corner, upper_right_corner, lower_right_corner, lower_left_corner, upper_left_corner]

            drawing = ImageDraw.Draw(framed_img)
            drawing.line(shape, width = self.border_thickness, fill = 'black')

        return framed_img
