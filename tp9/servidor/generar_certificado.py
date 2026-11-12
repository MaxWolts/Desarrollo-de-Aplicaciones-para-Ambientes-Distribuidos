"""
Genera un certificado TLS autofirmado para desarrollo (certs/cert.pem y certs/key.pem).
Valido para localhost y 127.0.0.1 durante 1 año.

Equivalente con OpenSSL:
  openssl req -x509 -newkey rsa:2048 -nodes -days 365 -keyout certs/key.pem -out certs/cert.pem
          -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
"""
import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CARPETA = Path(__file__).parent / "certs"


def generar():
    CARPETA.mkdir(exist_ok=True)

    # 1) par de claves RSA (privada + publica)
    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # 2) certificado X.509 firmado por la misma clave (autofirmado)
    nombre = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "TP9 Ambientes Distribuidos"),
    ])
    ahora = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(nombre)
        .issuer_name(nombre)  # emisor = sujeto -> autofirmado
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora - datetime.timedelta(minutes=5))
        .not_valid_after(ahora + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, key_encipherment=True, key_cert_sign=True,
            content_commitment=False, data_encipherment=False, key_agreement=False,
            crl_sign=False, encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(clave.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(clave.public_key()), critical=False)
        .sign(clave, hashes.SHA256())
    )

    (CARPETA / "key.pem").write_bytes(clave.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()))
    (CARPETA / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"[CERT] Certificado generado en {CARPETA} (valido hasta {cert.not_valid_after_utc:%d/%m/%Y})")


if __name__ == "__main__":
    generar()
