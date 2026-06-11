import potrace

def generate_svg(
    bitmap,
    output_svg
):
    path = potrace.Bitmap(bitmap).trace()

    with open(
        output_svg,
        "w"
    ) as f:

        f.write(
            '<svg xmlns="http://www.w3.org/2000/svg">'
        )

        for curve in path:

            start = curve.start_point

            f.write(
                f"<path d='M {start.x},{start.y}"
            )

            for segment in curve:
                end = segment.end_point

                f.write(
                    f" L {end.x},{end.y}"
                )

            f.write(
                "' fill='black'/>"
            )

        f.write("</svg>")