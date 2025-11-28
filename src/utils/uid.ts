import * as Crypto from 'expo-crypto';

export async function makeId(): Promise<string> {
  const random = Math.random().toString() + Date.now().toString();
  const hash = await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, random);
  return hash.slice(0, 16);
}

export async function makeUniqueKey(
  username: string | null,
  method: string,
  path: string,
  androidId: string | null,
  timestamp: number,
): Promise<string> {
  const str = `${username ?? ''}|${method}|${path}|${androidId ?? ''}|${timestamp}`;
  const hash = await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, str);
  return hash;
}
