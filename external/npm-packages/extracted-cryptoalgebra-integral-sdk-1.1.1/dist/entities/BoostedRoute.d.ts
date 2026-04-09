import { AnyToken } from '../types';
import { Currency } from './Currency';
import { Pool } from './pool';
import { Price } from './Price';
/**
 * Type of operation in a boosted route step
 */
export declare enum BoostedRouteStepType {
    /** ERC4626 deposit: underlying → shares */
    WRAP = "WRAP",
    /** ERC4626 redeem: shares → underlying */
    UNWRAP = "UNWRAP",
    /** AMM swap through pool */
    SWAP = "SWAP"
}
/**
 * Base properties shared by all step types
 */
interface BoostedRouteStepBase {
    /** Input token for this step */
    tokenIn: AnyToken;
    /** Output token for this step */
    tokenOut: AnyToken;
}
/**
 * WRAP step: ERC4626 deposit (underlying → shares)
 */
export interface BoostedRouteStepWrap extends BoostedRouteStepBase {
    type: BoostedRouteStepType.WRAP;
}
/**
 * UNWRAP step: ERC4626 redeem (shares → underlying)
 */
export interface BoostedRouteStepUnwrap extends BoostedRouteStepBase {
    type: BoostedRouteStepType.UNWRAP;
}
/**
 * SWAP step: AMM swap through pool
 */
export interface BoostedRouteStepSwap extends BoostedRouteStepBase {
    type: BoostedRouteStepType.SWAP;
    /** Pool used for swap (always present for SWAP type) */
    pool: Pool;
}
/**
 * A single step in a boosted route (discriminated union)
 */
export declare type BoostedRouteStep = BoostedRouteStepWrap | BoostedRouteStepUnwrap | BoostedRouteStepSwap;
/**
 * Represents a list of pools through which a boosted swap can occur
 * Supports wrapping/unwrapping logic for BoostedTokens (ERC4626)
 */
export declare class BoostedRoute<TInput extends Currency, TOutput extends Currency> {
    readonly pools: Pool[];
    readonly tokenPath: AnyToken[];
    readonly steps: BoostedRouteStep[];
    readonly input: TInput;
    readonly output: TOutput;
    readonly isBoosted: true;
    constructor(pools: Pool[], input: TInput, output: TOutput);
    private _midPrice;
    /**
     * Returns the mid price of the route
     *
     * NOTE: For BoostedRoute this returns a 1:1 stub price.
     * The real midPrice calculation requires async exchange rate fetching
     *
     */
    get midPrice(): Price<TInput, TOutput>;
    get chainId(): number;
}
export {};
