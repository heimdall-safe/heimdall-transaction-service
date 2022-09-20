# Generated by Django 3.0.4 on 2020-04-01 09:42

from django.db import migrations, models

from hexbytes import HexBytes

from gnosis.safe.safe_signature import (
    SafeSignature,
    SafeSignatureApprovedHash,
    SafeSignatureType,
)


def add_signature_type(apps, schema_editor):
    MultisigConfirmation = apps.get_model("history", "MultisigConfirmation")
    MultisigTransaction = apps.get_model("history", "MultisigTransaction")

    for multisig_confirmation in MultisigConfirmation.objects.all():
        if not multisig_confirmation.signature:  # It's an approvedHash
            multisig_confirmation.signature = SafeSignatureApprovedHash.build_for_owner(
                multisig_confirmation.owner,
                multisig_confirmation.multisig_transaction_hash,
            ).export_signature()

            multisig_confirmation.signature_type = SafeSignatureType.APPROVED_HASH.value
            multisig_confirmation.save(update_fields=["signature_type", "signature"])
        else:
            for safe_signature in SafeSignature.parse_signature(
                multisig_confirmation.signature,
                multisig_confirmation.multisig_transaction_hash,
            ):
                multisig_confirmation.signature_type = (
                    safe_signature.signature_type.value
                )
                multisig_confirmation.save(update_fields=["signature_type"])

    for multisig_tx in MultisigTransaction.objects.exclude(signatures=None):
        for safe_signature in SafeSignature.parse_signature(
            multisig_tx.signatures.tobytes(), HexBytes(multisig_tx.safe_tx_hash)
        ):
            multisig_confirmation, _ = MultisigConfirmation.objects.get_or_create(
                multisig_transaction_hash=multisig_tx.safe_tx_hash,
                owner=safe_signature.owner,
                defaults={
                    "ethereum_tx": None,
                    "multisig_transaction": multisig_tx,
                    "signature": safe_signature.export_signature(),
                    "signature_type": safe_signature.signature_type.value,
                },
            )
            if (
                multisig_confirmation.signature != safe_signature.export_signature()
                or multisig_confirmation.signature_type
                != safe_signature.signature_type.value
            ):

                multisig_confirmation.signature = safe_signature.export_signature()
                multisig_confirmation.signature_type = (
                    safe_signature.signature_type.value
                )
                multisig_confirmation.save(
                    update_fields=["signature", "signature_type"]
                )


class Migration(migrations.Migration):

    dependencies = [
        ("history", "0015_auto_20200327_1233"),
    ]

    operations = [
        migrations.AddField(
            model_name="multisigconfirmation",
            name="signature_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "CONTRACT_SIGNATURE"),
                    (1, "APPROVED_HASH"),
                    (2, "EOA"),
                    (3, "ETH_SIGN"),
                ],
                db_index=True,
                default=1,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(
            add_signature_type, reverse_code=migrations.RunPython.noop
        ),
    ]
