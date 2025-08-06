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

function composite(n, a, copy, two) {
  let value = binExp(a, copy, n);
  if (value === 1n || value === n - 1n) return false;
  for (let i = 0; i < two; i++) {
    value = (value * value) % n;
    if (value === n - 1n) return false;
  }
  return true;
}

function checkPrime(n) {
  if (n < 4n) return n === 2n || n === 3n;
  if (n % 2n === 0n) return false;

  let copy = n - 1n;
  let two = 0;
  while (copy % 2n === 0n) {
    copy /= 2n;
    two++;
  }

  const ITERATIONS = 50;
  const INT_MAX = 2n ** 31n;
  for (let i = 0; i < ITERATIONS; i++) {
    const a = 2n + BigInt(Math.floor(Math.random() * Number(INT_MAX))) % (n - 3n);
    if (composite(n, a, copy, two)) return false;
  }
  return true;
}

// Generate a large random BigInt in range [min, max]
function randBetween(min, max) {
  const range = max - min + 1n;
  const rand = BigInt(Math.floor(Math.random() * Number(range)));
  return min + rand;
}

async function findPrime() {
  let n1 = 10n ** 40n + randBetween(10n ** 30n, 10n ** 40n);
  let n2 = 10n ** 40n + randBetween(10n ** 30n, 10n ** 40n);

  while (!checkPrime(n1)) {
    n1++;
  }
  while (!checkPrime(n2)) {
    n2++;
  }
  return [n1, n2];
}

function n(x, y) {
  return x * y;
}

function gcd(a, b) {
  while (b !== 0n) {
    let t = b;
    b = a % b;
    a = t;
  }
  return a;
}

function carmichael(n1, n2) {
  n1 -= 1n;
  n2 -= 1n;
  return (n1 * n2) / gcd(n1, n2);
}

function findE(lamN) {
  let e = BigInt(Math.floor(Math.random() * Number(lamN - 1n)) + 1);
  while (gcd(e, lamN) !== 1n) {
    if (e < lamN - 1n) {
      e++;
    } else {
      e = BigInt(Math.floor(Math.random() * Number(lamN - 1n)) + 1);
    }
  }
  return e;
}

function gcdExtended(a, b) {
  if (a === 0n) return [b, 0n, 1n];
  let [gcdVal, x1, y1] = gcdExtended(b % a, a);
  let x = y1 - (b / a) * x1;
  let y = x1;
  return [gcdVal, x, y];
}

function findx(a, b) {
  let [, x, ] = gcdExtended(a, b);
  return (x + b) % b;
}


function decrypt(m) {
  let out = "";
  while (m > 0n) {
    out += String.fromCharCode(Number(m % 128n));
    m /= 128n;
    m = BigInt(Math.floor(Number(m)));
  }
  return out.split("").reverse().join("");
}

async function generateRSAKeys() {
  // Generate primes (smaller due to JS limitations)
  const [p, q] = await findPrime();

  const n_val = n(p, q);
  const lam_n = carmichael(p, q);
  const e = findE(lam_n);
  let d = findx(e, lam_n);

  return { n: n_val, e: e, d: d };
  

}
(async () => {
  const keys = await generateRSAKeys();
  console.log(keys);
})();