# ARM64 Support Strategy

## Current State

- **AWS EC2 Instance**: Currently using `t2.micro` (x86_64) due to container image limitations
- **Base Container**: Only built for `linux/amd64` (x86_64)
- **Goal**: Support `t4g.micro` (ARM64/Graviton) instances for free-tier AWS usage

## Why ARM64 Support Matters

1. **Free Tier**: `t4g.micro` (ARM64) is always free tier, same as `t2.micro` (x86_64)
2. **Performance**: ARM/Graviton instances often provide better price/performance
3. **Future-Proofing**: More cloud providers are offering ARM instances

## Strategy: Multi-Architecture Container Builds

### Phase 1: Update Base Container Build

**File**: `.github/workflows/build-api-container.yml`

**Change**: Update `platforms` to build for both architectures:
```yaml
platforms: linux/amd64,linux/arm64
```

**Benefits**:
- Single image supports both x86_64 and ARM64 hosts
- Docker automatically selects the correct architecture
- No changes needed to deployment playbooks

**Considerations**:
- Build times will increase (building for 2 architectures)
- Image size may increase slightly (multi-arch manifests)
- Need to verify all dependencies work on ARM64

### Phase 2: Verify Base Container Dependencies

Check that all Python packages in `containers/base/requirements.txt` support ARM64:
- Most common Python packages have ARM64 wheels or can compile
- Alpine Linux base image supports ARM64
- Test on actual ARM64 hardware or use QEMU emulation

### Phase 3: Update Other Containers (Optional)

Consider multi-arch for:
- `callableapis:status` - Status dashboard container
- `callableapis:services` - Services container (currently Java/Tomcat - check ARM64 support)

**Note**: Services container may need Java ARM64 builds if it doesn't already support it.

### Phase 4: Migration Path

When ready to switch to `t4g.micro`:

1. **Rebuild base container** with multi-arch support
2. **Update Terraform** (`terraform/aws_ec2_free_tier.tf`):
   - Change `instance_type` from `t2.micro` to `t4g.micro`
   - Update AMI filter from `x86_64` to `arm64`
3. **Apply Terraform** to recreate instance
4. **Redeploy base container** - Docker will automatically pull ARM64 version

### Implementation Checklist

- [ ] Update `.github/workflows/build-api-container.yml` to include `linux/arm64`
- [ ] Test base container build completes successfully for both architectures
- [ ] Verify base container runs correctly on ARM64 (test in staging or use QEMU)
- [ ] Update status container if needed (check if Flask/Python dependencies work on ARM64)
- [ ] Update services container if needed (check Java ARM64 support)
- [ ] Document any ARM64-specific considerations in deployment guides

### Testing Strategy

1. **Local Testing with QEMU**:
   ```bash
   docker run --rm --platform linux/arm64 rl337/callableapis:base
   ```

2. **GitHub Actions**: Already uses buildx which supports multi-arch

3. **Staging Deployment**: Deploy to a test ARM64 instance before production

### Rollback Plan

If ARM64 support causes issues:
- Revert workflow to `linux/amd64` only
- Keep `t2.micro` instances (always free tier)
- No deployment changes needed (already supports x86_64)

## Future Considerations

- **Services Container**: If Java/Tomcat doesn't support ARM64 well, may need to:
  - Keep services on x86_64 instances
  - Or use alternative Java runtime optimized for ARM
- **Build Performance**: Multi-arch builds take longer - consider:
  - Separating architectures into different workflows
  - Building ARM64 on demand vs. always
- **Provider Support**: Consider ARM64 support for:
  - Google Cloud (T2A instances)
  - Oracle Cloud (Ampere instances)
  - IBM Cloud (if ARM instances available)

## References

- Docker Multi-Architecture: https://docs.docker.com/build/building/multi-platform/
- AWS Graviton: https://aws.amazon.com/ec2/graviton/
- Alpine Linux ARM64: https://alpinelinux.org/downloads/

