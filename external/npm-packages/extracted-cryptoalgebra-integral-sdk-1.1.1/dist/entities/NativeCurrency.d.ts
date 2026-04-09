import { AbstractCurrency } from './AbstractCurrency';
/**
 * Represents the native currency of the chain on which it resides, e.g.
 */
export default abstract class NativeCurrency extends AbstractCurrency {
    readonly isNative: true;
    readonly isToken: false;
    readonly isBoosted: false;
}
