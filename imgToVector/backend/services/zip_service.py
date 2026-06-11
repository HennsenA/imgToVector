import zipfile

def create_zip(
    files,
    output
):
    with zipfile.ZipFile(
        output,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for file in files:
            zipf.write(file)