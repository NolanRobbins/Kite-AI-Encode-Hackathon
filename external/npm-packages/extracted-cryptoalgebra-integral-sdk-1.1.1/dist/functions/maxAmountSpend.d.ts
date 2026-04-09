import { Currency, CurrencyAmount } from "../entities";
/**
 * Given some token amount, return the max that can be spent of it
 * @param currencyAmount to return max of
 */
export declare function maxAmountSpend(currencyAmount?: CurrencyAmount<Currency>): CurrencyAmount<Currency> | undefined;
