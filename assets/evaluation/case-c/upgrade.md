# SYNTHETIC upgrade procedure for Widget CRD

The old release serves v1alpha1 and stores all objects as v1alpha1. The new v1 API changes spec.interval from a duration string ("30s") to integer seconds. This new release uses conversion strategy None. No webhook or other conversion process is implemented.

The documented upgrade job does these steps in order:
1. Set v1 storage:true and served:true; set v1alpha1 storage:false.
2. Patch status.storedVersions to ["v1"] immediately, without rewriting old objects.
3. Delete the v1alpha1 entry from spec.versions.

The supplied test suite uses a map-backed fake client and passes. It does not start an API server. There is no test exercising old stored objects or conversion. No data migration has been run. The release notes promise lossless upgrades from the old release.
