import { Currency } from './Currency';
import { AbstractCurrency } from './AbstractCurrency';
import { Token } from './Token';
import { AnyToken } from '../types';
/**
 * Represents an ERC4626-wrapped token ("boosted token") that corresponds
 * to an underlying ERC20 token and adds vault-like behavior.
 */
export declare class BoostedToken extends AbstractCurrency {
    readonly chainId: number;
    readonly address: string;
    /** The underlying ERC20 token (the "asset" in ERC4626 terms) */
    readonly underlying: Token;
    /** Flag to identify boosted tokens in runtime type checks */
    readonly isBoosted: true;
    readonly isToken: true;
    readonly isNative: false;
    constructor(chainId: number, address: string, decimals: number, symbol: string, name: string, underlying: Token);
    /**
     * Returns the underlying (unwrapped) ERC20 token.
     */
    get unwrapped(): Token;
    /**
     * For BoostedToken, wrapped should return itself (not the underlying).
     * This allows proper routing through boosted pools.
     */
    get wrapped(): BoostedToken;
    /**
     * Boosted tokens are not considered equal to their underlying asset,
     * but may share metadata (symbol/name) for UI display purposes.
     */
    equals(other: Currency): boolean;
    /**
     * Returns true if the address of this token sorts before the address of the other token
     * @param other other token to compare
     * @throws if the tokens have the same address
     * @throws if the tokens are on different chains
     */
    sortsBefore(other: AnyToken): boolean;
}
