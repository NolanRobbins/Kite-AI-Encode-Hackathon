import { Native } from './Native';
import { Token } from './Token';
export declare class ExtendedNative extends Native {
    private static _cachedNative;
    get wrapped(): Token;
    static onChain(chainId: number, symbol: string, name: string): ExtendedNative;
}
