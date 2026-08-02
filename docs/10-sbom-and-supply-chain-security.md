# Phase 7: SBOM and Supply Chain Security

## Objective

Implement SBOM generation and supply chain security in the Autonomous AI-Driven DevSecOps Engine.

The purpose of this phase is to generate a Software Bill of Materials for the Docker image, sign the image artifact, verify artifact integrity, and archive supply chain evidence inside Jenkins.

This phase improves software supply chain visibility by identifying all packages and dependencies inside the application image and validating that the image artifact has not been tampered with before continuing the CI/CD security workflow.

---

## Tool Used

The following tools were used in this phase:

```text
Syft
Cosign
Jenkins
Docker
```

Tool purpose:

| Tool | Purpose |
|---|---|
| Syft | Generates SBOM reports from the Docker image |
| CycloneDX | SBOM format used for component inventory |
| SPDX | SBOM format used for package and license metadata |
| Cosign | Signs and verifies image artifacts |
| Jenkins | Automates SBOM generation, signing, verification, and artifact archival |
| Docker | Builds and exports the target application image |

---

## Prerequisites

The following components were already completed before this phase:

* Jenkins CI/CD pipeline configured
* Docker image build working
* Trivy vulnerability scanning working
* OWASP ZAP DAST working
* DefectDojo report upload automation completed
* Jenkins credentials configured
* Reports directory ignored from GitHub
* Final Trivy CRITICAL vulnerability gate already validated

---

## Step-by-Step Configuration

## Step 1: Build Target Docker Image

The dummy UPI application Docker image was built before generating SBOM reports.

Project directory:

```text
/home/meet/projects/Autonomous-DevSecOps-Engine/autonomous-devsecops-engine
```

Command used:

```bash
cd ~/projects/Autonomous-DevSecOps-Engine/autonomous-devsecops-engine

docker build -t dummy-upi-app:latest ./dummy-upi-app
```

Target image:

```text
dummy-upi-app:latest
```

---

## Step 2: Generate CycloneDX SBOM using Syft

A CycloneDX SBOM report was generated using Syft.

Command used:

```bash
mkdir -p reports/sbom

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$PWD/reports/sbom:/reports" \
  anchore/syft:latest \
  dummy-upi-app:latest \
  -o cyclonedx-json=/reports/dummy-upi-app-cyclonedx.json
```

Generated file:

```text
reports/sbom/dummy-upi-app-cyclonedx.json
```

Verified result:

| Field | Value |
|---|---|
| Format | CycloneDX |
| Spec Version | 1.7 |
| File Size | 1.7 MB |
| Component Count | 3911 |

---

## Step 3: Generate SPDX SBOM using Syft

An SPDX SBOM report was also generated using Syft.

Command used:

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$PWD/reports/sbom:/reports" \
  anchore/syft:latest \
  dummy-upi-app:latest \
  -o spdx-json=/reports/dummy-upi-app-spdx.json
```

Generated file:

```text
reports/sbom/dummy-upi-app-spdx.json
```

Verified result:

| Field | Value |
|---|---|
| Format | SPDX |
| SPDX Version | SPDX-2.3 |
| File Size | 3.3 MB |
| Package Count | 507 |

---

## Step 4: Verify SBOM Reports

The generated SBOM reports were verified locally.

Verification result:

```text
FILE: reports/sbom/dummy-upi-app-cyclonedx.json
EXISTS: True
SIZE: 1662.45 KB
FORMAT: CycloneDX
SPEC VERSION: 1.7
COMPONENT COUNT: 3911

FILE: reports/sbom/dummy-upi-app-spdx.json
EXISTS: True
SIZE: 3371.11 KB
FORMAT: SPDX
SPDX VERSION: SPDX-2.3
PACKAGE COUNT: 507
```

This confirms that both SBOM formats were generated successfully.

---

## Step 5: Automate SBOM Generation in Jenkins

After successful manual validation, SBOM generation was automated inside the Jenkins pipeline.

Jenkins stage added:

```text
Generate SBOM Reports with Syft
```

The Jenkins stage performs the following actions:

```text
1. Creates reports/sbom directory
2. Generates CycloneDX SBOM
3. Generates SPDX SBOM
4. Validates that both files exist
5. Confirms CycloneDX format
6. Confirms SPDX format
7. Archives both SBOM reports as Jenkins artifacts
```

Jenkins-generated SBOM files:

```text
reports/sbom/dummy-upi-app-cyclonedx.json
reports/sbom/dummy-upi-app-spdx.json
```

Jenkins verification result:

```text
dummy-upi-app-cyclonedx.json   1.7M
dummy-upi-app-spdx.json        3.3M
SBOM artifacts verified successfully
```

Commit created:

```text
8d97894 ci: generate SBOM reports with Syft
```

---

## Step 6: Generate Cosign Key Pair

Cosign was used to generate a key pair for signing and verification.

Cosign key directory:

```text
.cosign/
```

Command used:

```bash
docker run --rm -it \
  --user root \
  -v "$PWD/.cosign:/cosign" \
  gcr.io/projectsigstore/cosign:latest \
  generate-key-pair \
  --output-key-prefix /cosign/cosign
```

Generated files:

```text
.cosign/cosign.key
.cosign/cosign.pub
```

Security note:

```text
.cosign/cosign.key is a private key and must never be committed to GitHub.
.cosign/cosign.pub is a public key used for signature verification.
The Cosign password must not be added to GitHub, documentation, screenshots, or Jenkinsfile.
```

---

## Step 7: Protect Cosign Keys

File ownership and permissions were fixed after key generation.

Commands used:

```bash
sudo chown -R "$USER:$USER" .cosign

chmod 700 .cosign
chmod 600 .cosign/cosign.key
chmod 644 .cosign/cosign.pub
```

The `.cosign/` directory was added to `.gitignore`.

Command used:

```bash
grep -q '^.cosign/$' .gitignore || echo '.cosign/' >> .gitignore
```

Commit created:

```text
7390444 chore: ignore cosign private keys
```

This protects the private signing key from accidental GitHub exposure.

---

## Step 8: Create Image Archive and Checksum

Because the Docker image was local and not yet pushed to a registry, the image was exported as a signable artifact.

Commands used:

```bash
mkdir -p reports/cosign

docker save dummy-upi-app:latest -o reports/cosign/dummy-upi-app-image.tar

sha256sum reports/cosign/dummy-upi-app-image.tar \
  | tee reports/cosign/dummy-upi-app-image.sha256
```

Generated files:

```text
reports/cosign/dummy-upi-app-image.tar
reports/cosign/dummy-upi-app-image.sha256
```

Checksum generated:

```text
58398a6cda52fb3b1232c7e6e0924bb672c302dbb44163088b451beeb0956178
```

---

## Step 9: Sign Image Artifact with Cosign

The Docker image archive was signed using Cosign.

Command used:

```bash
docker run --rm -it \
  --user root \
  -v "$PWD:/workspace" \
  gcr.io/projectsigstore/cosign:latest \
  sign-blob \
  --key /workspace/.cosign/cosign.key \
  --bundle /workspace/reports/cosign/dummy-upi-app-image.sigstore.json \
  /workspace/reports/cosign/dummy-upi-app-image.tar
```

Generated signature bundle:

```text
reports/cosign/dummy-upi-app-image.sigstore.json
```

---

## Step 10: Verify Cosign Signature

The signed image artifact was verified using the Cosign public key and signature bundle.

Command used:

```bash
docker run --rm \
  --user root \
  -v "$PWD:/workspace" \
  gcr.io/projectsigstore/cosign:latest \
  verify-blob \
  --key /workspace/.cosign/cosign.pub \
  --bundle /workspace/reports/cosign/dummy-upi-app-image.sigstore.json \
  /workspace/reports/cosign/dummy-upi-app-image.tar
```

A verification evidence file was created:

```text
reports/cosign/dummy-upi-app-signature-verification.txt
```

Verified result:

```text
Cosign Signature Verification: PASSED
Artifact: reports/cosign/dummy-upi-app-image.tar
Bundle: reports/cosign/dummy-upi-app-image.sigstore.json
Public Key: .cosign/cosign.pub
Result: Verified OK
```

---

## Step 11: Create Jenkins Credentials for Cosign

The following Jenkins credentials were created to automate Cosign signing and verification securely.

Credential 1:

| Field | Value |
|---|---|
| Kind | Secret file |
| File | cosign.key |
| ID | cosign-private-key |
| Purpose | Used to sign image artifact |

Credential 2:

| Field | Value |
|---|---|
| Kind | Secret file |
| File | cosign.pub |
| ID | cosign-public-key |
| Purpose | Used to verify image artifact signature |

Credential 3:

| Field | Value |
|---|---|
| Kind | Secret text |
| ID | cosign-key-password |
| Purpose | Password for Cosign private key |

Security note:

```text
The Cosign private key is stored in Jenkins Credentials.
The Cosign public key is stored in Jenkins Credentials.
The Cosign password is stored in Jenkins Credentials.
No Cosign key or password is hardcoded in the Jenkinsfile.
No Cosign key or password is committed to GitHub.
```

---

## Step 12: Automate Cosign Signing and Verification in Jenkins

A new Jenkins stage was added after SBOM generation.

Jenkins stage added:

```text
Sign and Verify Image Artifact with Cosign
```

The Jenkins stage performs the following actions:

```text
1. Downloads Cosign binary inside Jenkins workspace if missing
2. Loads Cosign private key from Jenkins secret file credential
3. Loads Cosign public key from Jenkins secret file credential
4. Loads Cosign password from Jenkins secret text credential
5. Saves Docker image as a signable archive
6. Generates SHA256 checksum
7. Signs the image archive using Cosign
8. Verifies the signature using Cosign
9. Creates verification evidence
10. Removes the large Docker image archive before artifact archival
```

Commit created:

```text
fbd6083 ci: add Cosign image signing verification
```

Generated Jenkins Cosign evidence files:

```text
reports/cosign/dummy-upi-app-image.sha256
reports/cosign/dummy-upi-app-image.sigstore.json
reports/cosign/cosign-verify-raw-output.txt
reports/cosign/dummy-upi-app-signature-verification.txt
```

---

## Verified Jenkins Result

Jenkins workspace was checked after the pipeline run.

Verification command:

```bash
docker exec -it jenkins bash -lc '
cd /var/jenkins_home/workspace/Autonomous-DevSecOps-Engine

echo "===== COSIGN REPORTS ====="
ls -lh reports/cosign

echo
echo "===== COSIGN VERIFICATION PROOF ====="
cat reports/cosign/dummy-upi-app-signature-verification.txt

echo
echo "===== SBOM REPORTS ====="
ls -lh reports/sbom
'
```

Verified Cosign reports:

```text
cosign-verify-raw-output.txt
dummy-upi-app-image.sha256
dummy-upi-app-image.sigstore.json
dummy-upi-app-signature-verification.txt
```

Verified Cosign proof:

```text
Cosign Signature Verification: PASSED
Artifact: dummy-upi-app:latest
Signed Artifact Type: Docker image archive
Bundle: reports/cosign/dummy-upi-app-image.sigstore.json
Checksum: reports/cosign/dummy-upi-app-image.sha256
Public Key Credential: cosign-public-key
Result: Verified OK
```

Verified SBOM reports:

```text
dummy-upi-app-cyclonedx.json   1.7M
dummy-upi-app-spdx.json        3.3M
```

---

## Final Pipeline Behavior

The Jenkins pipeline completed SBOM generation, Cosign signing, Cosign verification, DAST execution, and DefectDojo uploads before reaching the final Trivy CRITICAL gate.

The final Jenkins build failed at the Trivy CRITICAL gate because CRITICAL vulnerabilities were detected in the image.

Final gate result:

```text
dummy-upi-app:latest (debian 12.13)
Total: 7 (CRITICAL: 7)

Node.js (node-pkg)
Total: 2 (CRITICAL: 2)

Finished: FAILURE
```

This failure is expected security behavior and confirms that the pipeline blocks unsafe images after collecting and archiving security evidence.

---

## Evidence

The following evidence was validated during this phase:

| Evidence | Status |
|---|---|
| Manual CycloneDX SBOM generated | Verified |
| Manual SPDX SBOM generated | Verified |
| SBOM JSON validation completed | Verified |
| Jenkins Syft SBOM automation completed | Verified |
| Jenkins SBOM artifacts archived | Verified |
| Cosign key pair generated | Verified |
| Cosign private key protected | Verified |
| `.cosign/` added to `.gitignore` | Verified |
| Image archive checksum generated | Verified |
| Local Cosign signing completed | Verified |
| Local Cosign verification completed | Verified |
| Jenkins Cosign credentials created | Verified |
| Jenkins Cosign signing completed | Verified |
| Jenkins Cosign verification completed | Verified |
| Cosign verification evidence archived | Verified |
| Final Trivy CRITICAL gate triggered | Verified |

Screenshot evidence will be uploaded later under the `screenshots/` directory.

Recommended screenshot file names:

```text
screenshots/phase-07-syft-sbom-jenkins-artifacts.png
screenshots/phase-07-cosign-jenkins-verification.png
screenshots/phase-07-trivy-critical-gate-after-supply-chain.png
```

---

## Security Value Added

This phase adds software supply chain visibility and artifact integrity validation to the DevSecOps platform.

Benefits:

* Generates a complete dependency inventory for the Docker image
* Produces CycloneDX SBOM for security workflows
* Produces SPDX SBOM for package and license metadata
* Provides audit-ready SBOM evidence
* Signs the image artifact using Cosign
* Verifies image artifact integrity before later pipeline stages
* Stores Cosign keys securely in Jenkins Credentials
* Prevents private signing keys from being committed to GitHub
* Archives checksum, signature bundle, and verification evidence in Jenkins
* Supports future registry-based image signing with Harbor
* Strengthens Secure Software Development Lifecycle controls
