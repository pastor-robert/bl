#!/usr/bin/env python3

import argparse
from pypdf import PdfReader, PdfWriter, PageObject


def page_two_up(left: PageObject, right: PageObject) -> PageObject:
    """
    Prints two PageObjects in a 2-up format.

    Args:
        left: The first page to print.
        right: The second page to print.

    Returns:
        The merged PageObject representing the two pages printed 2-up.

    Create two blank pages
    >>> import pypdf as p
    >>> page1 = p.PageObject.create_blank_page(width=200, height=300)
    >>> page2 = p.PageObject.create_blank_page(width=200, height=300)

    Merge the pages
    >>> merged_page = page_two_up(page1, page2)

    Verify the result
    >>> assert isinstance(merged_page, PageObject)
    >>> assert merged_page.mediabox.width == 400
    >>> assert merged_page.mediabox.height == 300

    The two pages must be the same size
    # >>> page3 = p.PageObject.create_blank_page(width=200, height=400)
    # >>> page_two_up(page1, page3)
    # Traceback (most recent call last):
    #     ...
    # AssertionError: The two pages must be the same size
    #     ...
    """
    # Get the dimensions of the first page
    width = left.mediabox.width
    height = left.mediabox.height

    assert left.mediabox == right.mediabox, "The two pages must be the same size"

    # Create a new PageObject from the merged pages
    output_page = PageObject.create_blank_page(width=width * 2, height=height)
    output_page.merge_page(left)
    output_page.merge_translated_page(right, tx=width, ty=0)

    return output_page


def create_booklet(input_path: str, centerfold_path: str|None, output_path: str) -> None:
    """
    Converts a PDF document into booklet form. The resulting PDF will 
    contain half the number of pages as the input document, each page twice the size
    of the input pages. E.g., a 4-page 5.5x8.5 input document will result
    in a 2-page 8.5x11 booklet. When printed in flip-on-short-edge mode, the booklet
    made be folded in half to create a 5.5x8.5 booklet.

    If you have, say, a 6-page input document, you may add a centerfold. The centerfold
    will be added to the booklet after the first half of the input document, and before
    the second half. The centerfold must be the same size as the output document, i.e. 
    twice the size of the input document.

    Args:
        input_path (str): The path to the input PDF document.
        centerfold_path (str): The path to the centerfold PDF document. (optional)
        output_path (str): The path to save the output booklet PDF.

    Raises:
        FileNotFoundError: If the input file does not exist.
        AssertionError: If the input file has an odd number of pages.
        AssertionError: If the input file has variable page sizes.
    """
    # Create a new PDF writer
    pdf_writer = PdfWriter()

    # Copy the exterior pages
    with open(input_path, 'rb') as input_file:
        pdf_reader = PdfReader(input_file)
        total_pages = len(pdf_reader.pages)

        assert total_pages % 2 == 0, "The input PDF must have an even number of pages"

        for i in range(0, total_pages//2, 2):
            page = page_two_up(pdf_reader.pages[total_pages - i - 1], pdf_reader.pages[i])
            pdf_writer.add_page(page)
            i += 1
            if i < total_pages // 2:
                page = page_two_up(pdf_reader.pages[i], pdf_reader.pages[total_pages - i - 1])
                pdf_writer.add_page(page)

    # Copy the centerfold
    if centerfold_path:
        with open(centerfold_path, 'rb') as centerfold_file:
            pdf_reader = PdfReader(centerfold_file)
            angle = 90
            for page in pdf_reader.pages:
                page.rotate(angle)
                angle *= -1
                pdf_writer.add_page(page)

    # Save the booklet
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)


if __name__ == '__main__':
    """
    Usage: bl [-h] [-c CENTERFOLD] input_file output_file

    Convert a PDF document into booklet form. The resulting PDF will contain half the number
    of pages as the input document, each page twice the size of the input pages.
    E.g., a 4-page 5.5x8.5 input document will result in a 2-page 8.5x11 booklet.
    When printed in flip-on-short-edge mode, the booklet made be folded in half to
    create a 5.5x8.5 booklet.
    """

    parser = argparse.ArgumentParser(description='Convert a PDF document into booklet form.')
    parser.add_argument('-c', '--centerfold', help="Add FILE as a centerfold")
    parser.add_argument('input_file', help='Path to the input PDF document')
    parser.add_argument('output_file', help='Path to save the output booklet PDF')

    args = parser.parse_args()
    create_booklet(args.input_file, args.centerfold, args.output_file)