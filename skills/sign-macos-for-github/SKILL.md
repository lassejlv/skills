---
name: sign-macos-for-github
description: Set up Developer ID signing, Apple notarization, and GitHub Actions credentials for macOS apps distributed as DMG and ZIP downloads. Use when signing an app for GitHub releases, configuring Apple signing secrets, or fixing runner keychain failures.
---

# Sign macOS apps for GitHub

Carry the authorized setup through a credentialed GitHub build and downloaded-artifact verification. Reuse the account holder's existing credentials where possible. Keep Apple credential names independent of the product name so renaming the app needs no new certificate or API key. This skill may load automatically for macOS distribution-signing work.

## 1. Inspect the app and accounts

- Check the checkout, Git remote, dirty files, packaging scripts, release workflow, bundle identifier, architectures, nested executables, and entitlements. Preserve unrelated work.
- Confirm the intended Apple team in the signed-in Developer portal using available browser tools. Check `security find-identity -v -p codesigning` locally and GitHub authentication. Never pick a certificate merely because it is the first identity listed.
- Use **Developer ID Application** for direct app/DMG distribution. Apple Development and ad hoc signatures are for different purposes. A signed installer `.pkg` needs Developer ID Installer as well.
- Inspect existing credential exports in known local storage before creating replacements; don't print their contents. A `.cer` alone is insufficient: CI needs a password-protected `.p12` containing the certificate **and its private key**.

## 2. Obtain and verify credentials

If a usable certificate exists, export that identity and private key from Keychain Access as a protected `.p12`. Otherwise, create a CSR, issue a Developer ID Application certificate under the selected team, import the `.cer` into the keychain containing the CSR's private key, then export the identity.

For this workflow use an App Store Connect **Team API key**: its `.p8`, key ID, and issuer ID. Reuse a valid existing key; if absent, create one in App Store Connect under Users and Access → Integrations → App Store Connect API. Download and protect the private key immediately. Confirm the selected team before using any recovered key.

Verify the certificate's team and expiry, confirm its private key is available, then test notarization authentication:

```sh
xcrun notarytool history --key "$APPLE_NOTARY_KEY" \
  --key-id "$APPLE_NOTARY_KEY_ID" --issuer "$APPLE_NOTARY_ISSUER_ID"
```

A successful authentication check proves access, not successful notarization of this app. If a legacy P12 fails with Homebrew OpenSSL, try `/usr/bin/openssl`; do not replace valid credentials solely because a local legacy provider is missing.

## 3. Configure GitHub

Use the repository's existing credential contract if present; otherwise use these generic names:

| Setting | Kind | Value |
| --- | --- | --- |
| `APPLE_TEAM_ID` | Repository variable | Verified certificate's Apple team ID |
| `APPLE_CERTIFICATE_P12_BASE64` | Secret | Base64 `.p12` certificate and private key |
| `APPLE_CERTIFICATE_PASSWORD` | Secret | Password protecting that `.p12` |
| `APPLE_NOTARY_KEY_P8_BASE64` | Secret | Base64 Team API private key |
| `APPLE_NOTARY_KEY_ID` | Secret | API key ID |
| `APPLE_NOTARY_ISSUER_ID` | Secret | Issuer ID for that Apple team |

Upload through the GitHub connector or `gh secret set --repo "$REPO" NAME`, feeding values through stdin. Pipe file encoding directly into secret upload. Never echo credentials, enable shell tracing, commit key material, or attach it to artifacts. Store necessary recovery material outside the repository with restricted permissions.

## 4. Prepare the runner keychain

1. Validate required inputs; use `umask 077` and a temporary directory under `RUNNER_TEMP`. Register cleanup paths before any import can fail.
2. Decode the P12 and P8 there. Create and unlock a temporary keychain with a generated password; import the P12 with access for `codesign` and `security`.
3. Run `security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN"` for noninteractive private-key access.
4. **Add the temporary keychain to the user keychain search list, preserving existing entries.** Passing `codesign --keychain` alone did not resolve the private key on the verified GitHub runner; the import succeeded but signing failed until the search list was fixed.
5. Require exactly one valid Developer ID Application identity matching `APPLE_TEAM_ID`. Export its SHA-1 as `APPLE_SIGN_IDENTITY`, plus `APPLE_SIGNING_KEYCHAIN` and the decoded `APPLE_NOTARY_KEY` path, through `GITHUB_ENV`.
6. Add an `if: always()` cleanup step to delete the keychain and decoded credentials even on failure. Restore the original search list on persistent runners.

Keep secrets out of untrusted pull request jobs. Ordinary PR builds can use ad hoc signing; release jobs must fail when signing credentials are missing. Add a manual signed workflow run that uploads artifacts without publishing a release.

## 5. Sign, notarize, and package in order

1. Assemble the complete bundle. Sign nested code from the inside out, then the app, using Developer ID, `--options runtime`, and `--timestamp`. Preserve required runtime entitlements; for bundled Bun, inspect and retain its upstream JIT entitlements. Use `--deep` for verification, not as a substitute for signing each component.
2. Verify signatures, team, hardened runtime, and secure timestamps. Create a temporary ZIP of the signed app with `ditto -c -k --keepParent` and submit it with `xcrun notarytool submit … --wait --output-format json` using the API-key authentication above.
3. Require the returned status to be **Accepted**. For rejection, fetch `xcrun notarytool log SUBMISSION_ID` with the same authentication, fix the reported cause, and resubmit. For timeout, check the existing submission before starting another.
4. Staple and validate the app's ticket. Build the DMG containing that app, sign the DMG with Developer ID and a timestamp, submit it, require Accepted, then staple and validate the DMG.
5. Produce the final portable ZIP from the **stapled app**. ZIP files cannot be stapled directly. Generate checksums only after all signatures and tickets are final; do not mutate the signed app afterward.

## 6. Prove the distributed result

Run shell syntax checks, workflow validation (`actionlint` when available), and the app's relevant build/runtime checks. Push the prepared code before dispatching the signed workflow when GitHub setup is authorized. A successful local build is insufficient: verify the GitHub credential import, signing, notarization, artifact upload, and cleanup.

Download the workflow artifacts and validate their final checksums. Extract the ZIP and mount the DMG; check the app inside each. With `APP` and `DMG` pointing to the actual downloads:

```sh
codesign --display --verbose=4 "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"
xcrun stapler validate "$APP"
spctl --assess --type execute --verbose=2 "$APP"
codesign --verify --strict --verbose=2 "$DMG"
xcrun stapler validate "$DMG"
spctl --assess --type open --context context:primary-signature --verbose=2 "$DMG"
```

Check nested code's signing metadata and test its behavior, especially a bundled runtime that needs JIT. Launch the distributed app and exercise relevant functionality. Report the workflow URL, verified artifacts, and any untested architectures or first-run paths. Release publication and PR merging follow the user's scope; preparing signing does not itself authorize a new public release.

## Sources and worked example

- [Apple: Developer ID certificates](https://developer.apple.com/help/account/certificates/create-developer-id-certificates/)
- [Apple: Customizing the notarization workflow](https://developer.apple.com/documentation/security/customizing-the-notarization-workflow)
- [GitHub: Installing Apple certificates on macOS runners](https://docs.github.com/en/actions/how-tos/deploy/deploy-to-third-party-platforms/sign-xcode-applications)
- [Verified implementation and packaging scripts](https://github.com/lassejlv/sidedoor/pull/7), [credentialed workflow run](https://github.com/lassejlv/sidedoor/actions/runs/36770588783). Read the current target repository before adapting this example; no account IDs, private paths, or secrets are baked into this skill.
