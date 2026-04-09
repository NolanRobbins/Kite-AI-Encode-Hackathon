import { Price } from '../entities';
import { AnyToken } from '../types';
export declare function tryParsePrice(baseToken?: AnyToken, quoteToken?: AnyToken, value?: string): Price<AnyToken, AnyToken> | undefined;
export declare function tryParseTick(baseToken?: AnyToken, quoteToken?: AnyToken, value?: string, tickSpacing?: number): number | undefined;
