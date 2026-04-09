import { Currency, CurrencyAmount } from "../entities";
export declare const parseBalance: (value: string, decimals?: number) => import("@ethersproject/bignumber").BigNumber;
export declare function tryParseAmount<T extends Currency>(value?: string, currency?: T): CurrencyAmount<T> | undefined;
