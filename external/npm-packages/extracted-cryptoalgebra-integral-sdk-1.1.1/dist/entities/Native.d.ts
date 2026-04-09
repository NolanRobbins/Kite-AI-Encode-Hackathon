import { Token } from './Token';
import { Currency } from './Currency';
import NativeCurrency from './NativeCurrency';
/**
 * Native is the main usage of a 'native' currency
 */
export declare class Native extends NativeCurrency {
    protected constructor(chainId: number, symbol: string, name: string);
    get wrapped(): Token;
    private static _naitveCache;
    static onChain(chainId: number, symbol: string, name: string): Native;
    equals(other: Currency): boolean;
}
