function message(m) {
    let out = "";

    while (m > 0n) {  
        const charCode = Number(m % 128n);
        out += String.fromCharCode(charCode);
        m = m / 128n;
    }

    // Reverse the string
    out = out.split('').reverse().join('');

    return out;
}
function binExp(base, exponent, mod) {

  base = BigInt(base);
  exponent = BigInt(exponent);
  mod = BigInt(mod);

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


// Decrypt message
function RSA_decrypt(ciphertext,key,n_val){
  return message(binExp(ciphertext, key, n_val));
}