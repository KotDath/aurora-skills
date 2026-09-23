---
name: aurora-rpm-sign
description: Sign an existing Aurora OS RPM package with a developer key and certificate, handling an existing signature explicitly. Use for a built package from Qt, Flutter, Web, or another stack; not for building or validating package content.
---

# Sign an Aurora RPM

Sign the exact `.rpm` chosen by the user with `rpmsign-external`. Work from the package path, regardless of the framework that produced it. Speak in the user's language.

## Select artifact and credentials

Use a supplied RPM path or the exact artifact(s) produced by the current build workflow. Ask which one only when several unrelated versions or architectures remain plausible. Use key and certificate paths supplied by the user. For a development build, use `~/AuroraOS/package-signing/regular_key.pem` and `regular_cert.pem` when both exist and no other credentials were specified; these are public Regular development credentials. Do not choose them for a release request: use the user's personal key and certificate, or ask for their paths if missing. Keep key material outside the project and never display or copy private key contents. Let the signing tool prompt for an encrypted key's passphrase; do not put it in a command, log, or chat.

Find `rpmsign-external` on the host or through Aurora SDK Build Engine (`sfdk engine exec rpmsign-external`). For the latter, use the user's `sfdk` path or `~/AuroraOS/bin/sfdk`; ask for a path if the default is missing. Run `sfdk` from a directory inside its shared workspace. The RPM and credential files must be visible there too. Do not move credentials into that workspace without a user instruction.

## Handle an existing signature

Inspect the package with `rpmsign-external dump` before signing. If it is already signed, keep it and continue the workflow without asking, even when the broader task includes signing. Report the existing signer/profile when available; do not claim the signature is trusted solely because it exists. If the user explicitly requested replacing or forcing the signature, proceed immediately with `rpmsign-external sign --force` and the selected credentials; this changes the selected RPM in place unless the user chose another output. `--force` can remove existing developer and source signatures according to certificate type, so report that effect when a layered signature is present. If signature state cannot be determined and replacement was not requested, do not force it.

For an unsigned RPM in an authorized signing or end-to-end packaging workflow, use `rpmsign-external sign --key <key.pem> --cert <cert.pem> <rpm>` without another confirmation. By default, copy it to a sibling `signed/` directory under the same filename and sign that copy so the unsigned artifact remains available; follow a user-specified output path or in-place request instead. Handle all RPMs produced by the current build when the request covers those architectures, but do not sign unrelated files through `RPMS/*`. A request only to build or validate does not itself require signing.

After signing, inspect the result with `rpmsign-external dump`. Run `rpmsign-external verify --root-cert <ca.pem> <rpm>` when a trusted root certificate is available; otherwise report that trust verification was not completed. Return the signed RPM path and signature status. Content validation is a separate step.

See the official [package signing guide](https://developer.auroraos.ru/doc/sdk/app_development/packaging/package_signing) and [`rpmsign-external` commands](https://developer.auroraos.ru/doc/sdk/tools/rpmsign_external) for signature types, `--force`, and verification.
