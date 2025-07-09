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

console.log(RSA_decrypt(46508095479331127178250628908956324352266563929401325943577156143698653561611617,91574894897122706540006536371391524888683030334846024791689493900753672681618535692855959110927309300463677881571336374701061202789192470309821178305493496716530664351132591518459481583247910n,186206118512996995365151186218744230034979222335765854510926512584611447087039669
))