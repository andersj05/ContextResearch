# Unrestricted asymptotic parent-rate curve

October 2, 2026. Local analytic result, claim C67. The [proof](../../../research/UNRESTRICTED_RATE_CURVE_2026-10-02.md)
combines C66's complementary completion with an exact comparison of the six
complementary symmetry families. The unsigned family attains every positive-
slope supporting minimum. This extends C65's scalar optimization to the entire
unrestricted asymptotic curve under the unchanged uniform four-bit model.

There are 48 distinct integer polynomial comparisons, covering all 16 decision
words of each other family on three rational intervals whose union is [0,1].
After stripping positive factors (1-t), all interval-transformed coefficients
are nonnegative with strictly positive first and last coefficients. This is a
continuum proof for 0<t<1, not a dense numerical grid. The certificate retains
all columns outside the nearest-word witness's support. Public tables and
codebooks are fixed before source; source/parent/session/archive rereads stay
excluded. Heterogeneous tables and arbitrary joint parent encoders are allowed.

For every r>=0, D_infinity(r)=lim_k D_k(floor(k*r)) is the unsigned rate-
distortion curve. It runs from 1/2 at zero rate to 1/4 at
h_star=4-(5/8)*log2(5), and stays at 1/4 above h_star. Between them it is
parametrized by the optimal Gibbs channel, with a quadratic scalar root for its
balanced-word mass. Its support changes at about 0.620690001029 bits per block.
Mixing with a source-independent channel creates strict rate slack for coding
inside floor(k*r) bits. No finite optimal code or efficient encoder is supplied.

```powershell
python -m experiments.dependency_memory.rate_curve.certificate
python -m unittest discover -s experiments/dependency_memory -p test_curve.py -v
```

Only standard-library exact integer/rational arithmetic certifies the new
comparison. Independent tests execute source/query routes and check the
polynomial identities and Gibbs/slack calculations. Bounded post-hoc discovery
is preserved separately in [auxiliary](auxiliary/README.md), including an
unsuccessful two-witness screen. Frozen C33/C34/C65/C66 artifacts are unchanged.
Standard coding, strategies, averaging and polynomial-positivity methods are
not claimed new. External correctness and publication priority remain open;
zero new model calls, natural workflow episodes or production-cost results.
