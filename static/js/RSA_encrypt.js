function message(text) {
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
  console.log(text)
  console.log(typeof text)
  const m = message(text);

  console.log("m: " + m.toString())
  let result = binExp(m, BigInt(e), BigInt(n_val));
  console.log("result" + result);
  return result;
}

 console.log(RSA_encrypt('yessir',16223189244846157288064771169404082801295255039099112881546373679253265338859521n,186206118512996995365151186218744230034979222335765854510926512584611447087039669n))