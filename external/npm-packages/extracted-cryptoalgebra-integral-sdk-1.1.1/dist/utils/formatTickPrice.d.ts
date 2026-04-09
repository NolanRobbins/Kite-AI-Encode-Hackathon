import { Price, Token } from '../entities';
import { Bound } from "../enums/bound";
export declare function formatTickPrice(price: Price<Token, Token> | undefined, atLimit: {
    [bound in Bound]?: boolean | undefined;
}, direction: Bound, placeholder?: string): string;
