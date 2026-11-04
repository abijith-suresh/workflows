# Changelog

## [0.9.0](https://github.com/abijith-suresh/workflows/compare/0.8.1...v0.9.0) (2026-11-04)


### ⚠ BREAKING CHANGES

* **vercel-preview-cleanup:** use kebab-case inputs ([#51](https://github.com/abijith-suresh/workflows/issues/51))
* **release-please:** standardize on v-prefixed release tags ([#50](https://github.com/abijith-suresh/workflows/issues/50))

### Features

* **gate:** add a composite action for the caller gate job ([#52](https://github.com/abijith-suresh/workflows/issues/52)) ([92305dc](https://github.com/abijith-suresh/workflows/commit/92305dc27087e9070db52791752ca27e81003f8f))
* **release-please:** standardize on v-prefixed release tags ([#50](https://github.com/abijith-suresh/workflows/issues/50)) ([adb8a41](https://github.com/abijith-suresh/workflows/commit/adb8a41f4e42891de8d46c2dc91ae916d7786acc))
* **templates:** add caller files and shared default configs ([#54](https://github.com/abijith-suresh/workflows/issues/54)) ([6a3488b](https://github.com/abijith-suresh/workflows/commit/6a3488b94ef4c7db889693de0f73a40e51642e48))
* **vercel-preview-cleanup:** use kebab-case inputs ([#51](https://github.com/abijith-suresh/workflows/issues/51)) ([a3a3e43](https://github.com/abijith-suresh/workflows/commit/a3a3e435a0dfc1465be8c762d9178229f963a8dc))


### Bug Fixes

* **ci:** update checkout to v7.0.1 and mise-action to v5.2.6 ([#49](https://github.com/abijith-suresh/workflows/issues/49)) ([8d3ee4c](https://github.com/abijith-suresh/workflows/commit/8d3ee4c02b697d106b8a6fcda5882c9de127c7bf))

## [0.8.1](https://github.com/abijith-suresh/workflows/compare/0.8.0...0.8.1) (2026-10-09)


### Bug Fixes

* **vercel-preview-cleanup:** parse inspect output without merged stderr ([#42](https://github.com/abijith-suresh/workflows/issues/42)) ([bf88c64](https://github.com/abijith-suresh/workflows/commit/bf88c64c1bb4933e94b723073c790dca0d9d2fa8))

## [0.8.0](https://github.com/abijith-suresh/workflows/compare/0.7.0...0.8.0) (2026-10-09)


### Features

* **ci:** run Dependabot auto-merge without a stored token ([#39](https://github.com/abijith-suresh/workflows/issues/39)) ([b324658](https://github.com/abijith-suresh/workflows/commit/b32465858c3527d222a7118fbbb1cbd5ccad4611))

## [0.7.0](https://github.com/abijith-suresh/workflows/compare/0.6.0...0.7.0) (2026-10-08)


### Features

* **ci:** add strict Astro CI pipeline ([#38](https://github.com/abijith-suresh/workflows/issues/38)) ([a6976e4](https://github.com/abijith-suresh/workflows/commit/a6976e4370eb048119c7196bd95be57838788dee))


### Bug Fixes

* **ci:** guard Vercel cleanup and scope tokens ([#34](https://github.com/abijith-suresh/workflows/issues/34)) ([0424bd4](https://github.com/abijith-suresh/workflows/commit/0424bd486ad1c3e0bbb4d206886dec114872eb68))
* **ci:** recheck edited titles and distinguish release caller ([#31](https://github.com/abijith-suresh/workflows/issues/31)) ([9aebd56](https://github.com/abijith-suresh/workflows/commit/9aebd5663824c322d973105bcb0dcf303cc2a15c))

## [0.6.0](https://github.com/abijith-suresh/workflows/compare/0.5.0...0.6.0) (2026-09-29)


### Features

* **ci:** add release branches and shared Dependabot workflow ([#27](https://github.com/abijith-suresh/workflows/issues/27)) ([d7b0eb2](https://github.com/abijith-suresh/workflows/commit/d7b0eb28b32923b160fb2656e8d18cf60f85724d))
* **ci:** add reusable Vercel preview cleanup workflow ([#28](https://github.com/abijith-suresh/workflows/issues/28)) ([cb55685](https://github.com/abijith-suresh/workflows/commit/cb5568503a77dd1d70d531e5d902d7865a897645))

## [0.5.0](https://github.com/abijith-suresh/workflows/compare/v0.4.1...0.5.0) (2026-09-18)


### ⚠ BREAKING CHANGES

* **ci:** reusable release-please with no-v tags ([#22](https://github.com/abijith-suresh/workflows/issues/22))
* **ci:** read Node and npm versions from mise.toml ([#21](https://github.com/abijith-suresh/workflows/issues/21))

### Features

* **ci:** read Node and npm versions from mise.toml ([#21](https://github.com/abijith-suresh/workflows/issues/21)) ([0360a8a](https://github.com/abijith-suresh/workflows/commit/0360a8a437497c1589dcd12dea32f432cb6dc64c))
* **ci:** reusable release-please with no-v tags ([#22](https://github.com/abijith-suresh/workflows/issues/22)) ([91910de](https://github.com/abijith-suresh/workflows/commit/91910de008d024aba8ef1b0035fbf5406ff085b2))


### Bug Fixes

* **ci:** harden mise.toml Bun version parsing ([#20](https://github.com/abijith-suresh/workflows/issues/20)) ([f9cb333](https://github.com/abijith-suresh/workflows/commit/f9cb333731cac5813cee2868a99e6715408f9bee))
* **ci:** set persist-credentials false on checkouts ([#19](https://github.com/abijith-suresh/workflows/issues/19)) ([e363630](https://github.com/abijith-suresh/workflows/commit/e363630154f38452436c9506f22012dd680ea0da))

## [0.4.1](https://github.com/abijith-suresh/workflows/compare/v0.4.0...v0.4.1) (2026-09-17)


### Bug Fixes

* **ci:** use mise as the only Bun version source ([#17](https://github.com/abijith-suresh/workflows/issues/17)) ([0ef06ee](https://github.com/abijith-suresh/workflows/commit/0ef06ee51921f5861dca1258485ea25b8eb14746))

## [0.4.0](https://github.com/abijith-suresh/workflows/compare/v0.3.0...v0.4.0) (2026-09-05)


### ⚠ BREAKING CHANGES

* **ci:** read Bun version from root mise.toml ([#15](https://github.com/abijith-suresh/workflows/issues/15))

### Features

* **ci:** read Bun version from root mise.toml ([#15](https://github.com/abijith-suresh/workflows/issues/15)) ([1954c96](https://github.com/abijith-suresh/workflows/commit/1954c96389166f2d0e54a9a94df174270f3ba27a))

## [0.3.0](https://github.com/abijith-suresh/workflows/compare/v0.2.0...v0.3.0) (2026-08-03)


### ⚠ BREAKING CHANGES

* **ci:** enforce workflow contracts and rename title check ([#11](https://github.com/abijith-suresh/workflows/issues/11))
* **ci:** standardize Bun quality contract ([#9](https://github.com/abijith-suresh/workflows/issues/9))

### Features

* **ci:** enforce workflow contracts and rename title check ([#11](https://github.com/abijith-suresh/workflows/issues/11)) ([eec1607](https://github.com/abijith-suresh/workflows/commit/eec1607aa65f419c67498b1e39cbb4ce72e8db41))
* **ci:** standardize Bun quality contract ([#9](https://github.com/abijith-suresh/workflows/issues/9)) ([158b22b](https://github.com/abijith-suresh/workflows/commit/158b22b74fbf4cf11c2e2caea2c58d28547ae336))

## [0.2.0](https://github.com/abijith-suresh/workflows/compare/v0.1.0...v0.2.0) (2026-08-03)


### Features

* **ci:** add reusable npm quality workflow ([#7](https://github.com/abijith-suresh/workflows/issues/7)) ([731aec9](https://github.com/abijith-suresh/workflows/commit/731aec983c8bd78635d5d69074c47ffc74f46bf0))

## [0.1.0](https://github.com/abijith-suresh/workflows/compare/v0.0.1...v0.1.0) (2026-08-02)


### Features

* **ci:** add reusable dependency review workflow ([#5](https://github.com/abijith-suresh/workflows/issues/5)) ([d47573a](https://github.com/abijith-suresh/workflows/commit/d47573a18810d3ce069939b683a8d7eaa7304267))

## [0.0.1]

- Initial reusable workflow foundation.
