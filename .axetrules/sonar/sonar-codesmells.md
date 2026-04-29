# Sonar Code Smells
Source: response.json
Total issues (code smells): 233
Blocker: 3, Critical: 9, Major: 0, Minor: 0
Generated: 2026-04-23T15:45:32Z

## BLOCKER

- [x] BLOCKER | java:S2187 | src/test/java/com/carrefour/atuin/invoice/factory/ReportBodyFactoryImplTest.java:L33 | Add some tests to this class.
  - Detalle: Add some tests to this class.
  - Recomendación: Ver regla java:S2187 en SonarQube
  - IssueKey: AZ25dEclvvdTC0s_wPPq
  - Tags: confusing, junit, tests, unused
  - Esfuerzo estimado: N/A
  - Commit (sugerido): test: add assertions for ReportBodyFactoryImpl build
  - Patch (sugerido): AZ25dEclvvdTC0s_wPPq.patch
  - Cambios: Se reactivó/añadió un test con aserciones para `ReportBodyFactoryImpl.build(...)` e inicialización de mocks.

- [ ] BLOCKER | java:S2187 | src/test/java/com/carrefour/atuin/invoice/service/imp/FTPServiceImplTest.java:L36 | Add some tests to this class.
  - Detalle: Add some tests to this class.
  - Recomendación: Ver regla java:S2187 en SonarQube
  - IssueKey: AZ25dEb5vvdTC0s_wPPQ
  - Tags: confusing, junit, tests, unused
  - Esfuerzo estimado: N/A

- [ ] BLOCKER | java:S2699 | src/test/java/com/carrefour/atuin/invoice/service/imp/ReportServiceImplTest.java:L181 | Add at least one assertion to this test case.
  - Detalle: Add at least one assertion to this test case.
  - Recomendación: Ver regla java:S2699 en SonarQube
  - IssueKey: AZ25dEccvvdTC0s_wPPY
  - Tags: junit, tests
  - Esfuerzo estimado: N/A

## CRITICAL

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/service/impl/InvoiceServiceImpl.java:L325 | Refactor this method to reduce its Cognitive Complexity from 17 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 17 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZnN4F6b_pWZoElQsWj8
  - Tags: brain-overload
  - Esfuerzo estimado: 7min

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/factory/impl/InvoiceFactoryImpl.java:L158 | Refactor this method to reduce its Cognitive Complexity from 20 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 20 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZl9XAxf_pWZoElQmtNq
  - Tags: brain-overload
  - Esfuerzo estimado: 10min

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/factory/impl/InvoiceFactoryImpl.java:L317 | Refactor this method to reduce its Cognitive Complexity from 26 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 26 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZl9XAxf_pWZoElQmtNs
  - Tags: brain-overload
  - Esfuerzo estimado: 16min

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/factory/impl/InvoiceFactoryImpl.java:L433 | Refactor this method to reduce its Cognitive Complexity from 25 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 25 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZl9XAxf_pWZoElQmtNu
  - Tags: brain-overload
  - Esfuerzo estimado: 15min

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/factory/impl/InvoiceFactoryImpl.java:L591 | Refactor this method to reduce its Cognitive Complexity from 16 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 16 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZl9XAxf_pWZoElQmtNw
  - Tags: brain-overload
  - Esfuerzo estimado: 6min

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/factory/impl/InvoiceFactoryImpl.java:L858 | Refactor this method to reduce its Cognitive Complexity from 48 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 48 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZl9XAxf_pWZoElQmtNx
  - Tags: brain-overload
  - Esfuerzo estimado: 38min

- [ ] CRITICAL | java:S3776 | src/main/java/com/carrefour/atuin/invoice/factory/impl/ReportBodyFactoryImpl.java:L254 | Refactor this method to reduce its Cognitive Complexity from 24 to the 15 allowed.
  - Detalle: Refactor this method to reduce its Cognitive Complexity from 24 to the 15 allowed.
  - Recomendación: Ver regla java:S3776 en SonarQube
  - IssueKey: AZl9XAu-_pWZoElQmtNb
  - Tags: brain-overload
  - Esfuerzo estimado: 14min

- [ ] CRITICAL | java:S131 | src/main/java/com/carrefour/atuin/invoice/factory/impl/TaskExecutionHandlerFactoryImpl.java:L33 | Add a default case to this switch.
  - Detalle: Add a default case to this switch.
  - Recomendación: Ver regla java:S131 en SonarQube
  - IssueKey: AZl9XAv9_pWZoElQmtNk
  - Tags: cert, cwe
  - Esfuerzo estimado: 5min

- [ ] CRITICAL | java:S1192 | src/main/java/com/carrefour/atuin/reports/services/impl/JasperReportGenerator.java:L103 | Define a constant instead of duplicating this literal ".jasper" 3 times.
  - Detalle: Define a constant instead of duplicating this literal ".jasper" 3 times.
  - Recomendación: Ver regla java:S1192 en SonarQube
  - IssueKey: AZl9XA9r_pWZoElQmtQD
  - Tags: design
  - Esfuerzo estimado: 8min

## Nota
Los issues se corregirán en iteraciones, entregando parches (unified diff) y commits atómicos por cada issue.
