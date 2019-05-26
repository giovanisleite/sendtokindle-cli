import argparse
import base64
import os

from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId
)

EXTENSIONS_MIMETYPES = {
    '.mobi': 'application/x-mobipocket-ebook',
    '.epub': 'application/epub+zip',
    '.doc': 'application/epub+zip',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.azw': 'application/vnd.amazon.ebook',
    '.pdf': 'application/pdf'
}


def main():
    filepath, convert = parse_args()
    email = build_email(convert)
    attachment = build_attachment(filepath)
    send_email(email, attachment)


def build_email(convert=False):
    return Mail(
        from_email=config('FROM_EMAIL'),
        to_emails=config('TO_EMAIL'),
        subject=' ',
        html_content='CONVERT' if convert else ' ',
    )


def build_attachment(file_path, disposition="attachment", content_id="Ebook"):
    filename, file_type, content = file_info(file_path)

    attachment = Attachment()
    attachment.file_content = FileContent(content)
    attachment.file_type = FileType(file_type)
    attachment.file_name = FileName(filename)
    attachment.disposition = Disposition(disposition)
    attachment.content_id = ContentId(content_id)

    return attachment


def send_email(email, attachment):
    email.attachment = attachment
    sg = SendGridAPIClient(config('SENDGRID_KEY'))
    try:
        response = sg.send(email)
        return 200 <= response.status_code <= 299
    except Exception as e:
        print(e)


def file_info(file_path):
    filename = os.path.basename(file_path)
    *_, extension = os.path.splitext(file_path)
    file_type = EXTENSIONS_MIMETYPES[extension]

    with open(file_path, 'rb') as f:
        data = f.read()
    content = base64.b64encode(data).decode()

    return filename, file_type, content


def parse_args():
    parser = argparse.ArgumentParser(
        description='Envie arquivos para seu kindle'
    )
    parser.add_argument(
        'filepath',
        type=str,
        help=('Caminho do arquivo a ser enviado. '
              '(Substitua ~/ por /home/SEU_NOME_DE_USUARIO/)')
    )
    parser.add_argument(
        '--convert',
        dest='convert',
        action='store_const',
        const=True,
        default=False,
        help=('PDFs podem ser convertidos para o formato próprio do kindle, '
              'assim você pode usar funções como tamanho da fonte e anotações')
    )
    args = parser.parse_args()
    return args.filepath, args.convert


if __name__ == "__main__":
    main()
