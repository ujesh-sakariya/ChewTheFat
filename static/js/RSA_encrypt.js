function message(text) {
  let m = 0n;
  for (let char of text) {
    m = m * 128n + BigInt(char.charCodeAt(0));
  }
  return m;
}
// Utility for big integers - use native BigInt (ES2020+)
function binExp(base, exponent, mod) {
  if (mod === 0n) throw new Error("mod argument should not be 0");
  let out = 1n;
  base = base % mod;
  let current = base;
  while (exponent !== 0n) {
    if (exponent % 2n === 1n) {
      out = (out * current) % mod;
    }
    current = (current * current) % mod;
    exponent /= 2n;
    exponent = exponent >> 0n; // force integer division
  }
  return out;
}

function RSA_encrypt(m,e,n_val) {
  // Encrypt message
  return  binExp(m, e, n_val);

}