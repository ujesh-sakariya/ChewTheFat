function myMessage(text) {
  let m = 0n;

  for (let char of text) {
    m = m * 128n + BigInt(char.charCodeAt(0));

  }
  return m;
}

function binExp(base, exponent, mod) {
  // Ensure all arguments are BigInt
  base = BigInt(base);
  exponent = BigInt(exponent);
  mod = BigInt(mod);

  if (mod === 0n) throw new Error("mod argument should not be 0");
  let out = 1n;
  base = base % mod;

  while (exponent !== 0n) {
    if (exponent % 2n === 1n) {
      out = (out * base) % mod;
    }
    base = (base * base) % mod;
    exponent = exponent / 2n;
  }
  return out;
}

function RSA_encrypt(text, e, n_val) {
  const m = myMessage(text);
  let result = binExp(m, BigInt(e), BigInt(n_val));
  return result;
}

