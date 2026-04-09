import JSBI from 'jsbi';
import invariant from 'tiny-invariant';
import { defaultAbiCoder, Interface } from '@ethersproject/abi';
import { getAddress, getCreate2Address } from '@ethersproject/address';
import { keccak256, pack } from '@ethersproject/solidity';
import { keccak256 as keccak256$1 } from '@ethersproject/keccak256';
import { concat, zeroPad } from '@ethersproject/bytes';
import { toUtf8Bytes } from '@ethersproject/strings';
import _Big from 'big.js';
import toFormat from 'toformat';
import _Decimal from 'decimal.js-light';
import { parseUnits } from '@ethersproject/units';

function _regeneratorRuntime() {
  _regeneratorRuntime = function () {
    return e;
  };
  var t,
    e = {},
    r = Object.prototype,
    n = r.hasOwnProperty,
    o = Object.defineProperty || function (t, e, r) {
      t[e] = r.value;
    },
    i = "function" == typeof Symbol ? Symbol : {},
    a = i.iterator || "@@iterator",
    c = i.asyncIterator || "@@asyncIterator",
    u = i.toStringTag || "@@toStringTag";
  function define(t, e, r) {
    return Object.defineProperty(t, e, {
      value: r,
      enumerable: !0,
      configurable: !0,
      writable: !0
    }), t[e];
  }
  try {
    define({}, "");
  } catch (t) {
    define = function (t, e, r) {
      return t[e] = r;
    };
  }
  function wrap(t, e, r, n) {
    var i = e && e.prototype instanceof Generator ? e : Generator,
      a = Object.create(i.prototype),
      c = new Context(n || []);
    return o(a, "_invoke", {
      value: makeInvokeMethod(t, r, c)
    }), a;
  }
  function tryCatch(t, e, r) {
    try {
      return {
        type: "normal",
        arg: t.call(e, r)
      };
    } catch (t) {
      return {
        type: "throw",
        arg: t
      };
    }
  }
  e.wrap = wrap;
  var h = "suspendedStart",
    l = "suspendedYield",
    f = "executing",
    s = "completed",
    y = {};
  function Generator() {}
  function GeneratorFunction() {}
  function GeneratorFunctionPrototype() {}
  var p = {};
  define(p, a, function () {
    return this;
  });
  var d = Object.getPrototypeOf,
    v = d && d(d(values([])));
  v && v !== r && n.call(v, a) && (p = v);
  var g = GeneratorFunctionPrototype.prototype = Generator.prototype = Object.create(p);
  function defineIteratorMethods(t) {
    ["next", "throw", "return"].forEach(function (e) {
      define(t, e, function (t) {
        return this._invoke(e, t);
      });
    });
  }
  function AsyncIterator(t, e) {
    function invoke(r, o, i, a) {
      var c = tryCatch(t[r], t, o);
      if ("throw" !== c.type) {
        var u = c.arg,
          h = u.value;
        return h && "object" == typeof h && n.call(h, "__await") ? e.resolve(h.__await).then(function (t) {
          invoke("next", t, i, a);
        }, function (t) {
          invoke("throw", t, i, a);
        }) : e.resolve(h).then(function (t) {
          u.value = t, i(u);
        }, function (t) {
          return invoke("throw", t, i, a);
        });
      }
      a(c.arg);
    }
    var r;
    o(this, "_invoke", {
      value: function (t, n) {
        function callInvokeWithMethodAndArg() {
          return new e(function (e, r) {
            invoke(t, n, e, r);
          });
        }
        return r = r ? r.then(callInvokeWithMethodAndArg, callInvokeWithMethodAndArg) : callInvokeWithMethodAndArg();
      }
    });
  }
  function makeInvokeMethod(e, r, n) {
    var o = h;
    return function (i, a) {
      if (o === f) throw new Error("Generator is already running");
      if (o === s) {
        if ("throw" === i) throw a;
        return {
          value: t,
          done: !0
        };
      }
      for (n.method = i, n.arg = a;;) {
        var c = n.delegate;
        if (c) {
          var u = maybeInvokeDelegate(c, n);
          if (u) {
            if (u === y) continue;
            return u;
          }
        }
        if ("next" === n.method) n.sent = n._sent = n.arg;else if ("throw" === n.method) {
          if (o === h) throw o = s, n.arg;
          n.dispatchException(n.arg);
        } else "return" === n.method && n.abrupt("return", n.arg);
        o = f;
        var p = tryCatch(e, r, n);
        if ("normal" === p.type) {
          if (o = n.done ? s : l, p.arg === y) continue;
          return {
            value: p.arg,
            done: n.done
          };
        }
        "throw" === p.type && (o = s, n.method = "throw", n.arg = p.arg);
      }
    };
  }
  function maybeInvokeDelegate(e, r) {
    var n = r.method,
      o = e.iterator[n];
    if (o === t) return r.delegate = null, "throw" === n && e.iterator.return && (r.method = "return", r.arg = t, maybeInvokeDelegate(e, r), "throw" === r.method) || "return" !== n && (r.method = "throw", r.arg = new TypeError("The iterator does not provide a '" + n + "' method")), y;
    var i = tryCatch(o, e.iterator, r.arg);
    if ("throw" === i.type) return r.method = "throw", r.arg = i.arg, r.delegate = null, y;
    var a = i.arg;
    return a ? a.done ? (r[e.resultName] = a.value, r.next = e.nextLoc, "return" !== r.method && (r.method = "next", r.arg = t), r.delegate = null, y) : a : (r.method = "throw", r.arg = new TypeError("iterator result is not an object"), r.delegate = null, y);
  }
  function pushTryEntry(t) {
    var e = {
      tryLoc: t[0]
    };
    1 in t && (e.catchLoc = t[1]), 2 in t && (e.finallyLoc = t[2], e.afterLoc = t[3]), this.tryEntries.push(e);
  }
  function resetTryEntry(t) {
    var e = t.completion || {};
    e.type = "normal", delete e.arg, t.completion = e;
  }
  function Context(t) {
    this.tryEntries = [{
      tryLoc: "root"
    }], t.forEach(pushTryEntry, this), this.reset(!0);
  }
  function values(e) {
    if (e || "" === e) {
      var r = e[a];
      if (r) return r.call(e);
      if ("function" == typeof e.next) return e;
      if (!isNaN(e.length)) {
        var o = -1,
          i = function next() {
            for (; ++o < e.length;) if (n.call(e, o)) return next.value = e[o], next.done = !1, next;
            return next.value = t, next.done = !0, next;
          };
        return i.next = i;
      }
    }
    throw new TypeError(typeof e + " is not iterable");
  }
  return GeneratorFunction.prototype = GeneratorFunctionPrototype, o(g, "constructor", {
    value: GeneratorFunctionPrototype,
    configurable: !0
  }), o(GeneratorFunctionPrototype, "constructor", {
    value: GeneratorFunction,
    configurable: !0
  }), GeneratorFunction.displayName = define(GeneratorFunctionPrototype, u, "GeneratorFunction"), e.isGeneratorFunction = function (t) {
    var e = "function" == typeof t && t.constructor;
    return !!e && (e === GeneratorFunction || "GeneratorFunction" === (e.displayName || e.name));
  }, e.mark = function (t) {
    return Object.setPrototypeOf ? Object.setPrototypeOf(t, GeneratorFunctionPrototype) : (t.__proto__ = GeneratorFunctionPrototype, define(t, u, "GeneratorFunction")), t.prototype = Object.create(g), t;
  }, e.awrap = function (t) {
    return {
      __await: t
    };
  }, defineIteratorMethods(AsyncIterator.prototype), define(AsyncIterator.prototype, c, function () {
    return this;
  }), e.AsyncIterator = AsyncIterator, e.async = function (t, r, n, o, i) {
    void 0 === i && (i = Promise);
    var a = new AsyncIterator(wrap(t, r, n, o), i);
    return e.isGeneratorFunction(r) ? a : a.next().then(function (t) {
      return t.done ? t.value : a.next();
    });
  }, defineIteratorMethods(g), define(g, u, "Generator"), define(g, a, function () {
    return this;
  }), define(g, "toString", function () {
    return "[object Generator]";
  }), e.keys = function (t) {
    var e = Object(t),
      r = [];
    for (var n in e) r.push(n);
    return r.reverse(), function next() {
      for (; r.length;) {
        var t = r.pop();
        if (t in e) return next.value = t, next.done = !1, next;
      }
      return next.done = !0, next;
    };
  }, e.values = values, Context.prototype = {
    constructor: Context,
    reset: function (e) {
      if (this.prev = 0, this.next = 0, this.sent = this._sent = t, this.done = !1, this.delegate = null, this.method = "next", this.arg = t, this.tryEntries.forEach(resetTryEntry), !e) for (var r in this) "t" === r.charAt(0) && n.call(this, r) && !isNaN(+r.slice(1)) && (this[r] = t);
    },
    stop: function () {
      this.done = !0;
      var t = this.tryEntries[0].completion;
      if ("throw" === t.type) throw t.arg;
      return this.rval;
    },
    dispatchException: function (e) {
      if (this.done) throw e;
      var r = this;
      function handle(n, o) {
        return a.type = "throw", a.arg = e, r.next = n, o && (r.method = "next", r.arg = t), !!o;
      }
      for (var o = this.tryEntries.length - 1; o >= 0; --o) {
        var i = this.tryEntries[o],
          a = i.completion;
        if ("root" === i.tryLoc) return handle("end");
        if (i.tryLoc <= this.prev) {
          var c = n.call(i, "catchLoc"),
            u = n.call(i, "finallyLoc");
          if (c && u) {
            if (this.prev < i.catchLoc) return handle(i.catchLoc, !0);
            if (this.prev < i.finallyLoc) return handle(i.finallyLoc);
          } else if (c) {
            if (this.prev < i.catchLoc) return handle(i.catchLoc, !0);
          } else {
            if (!u) throw new Error("try statement without catch or finally");
            if (this.prev < i.finallyLoc) return handle(i.finallyLoc);
          }
        }
      }
    },
    abrupt: function (t, e) {
      for (var r = this.tryEntries.length - 1; r >= 0; --r) {
        var o = this.tryEntries[r];
        if (o.tryLoc <= this.prev && n.call(o, "finallyLoc") && this.prev < o.finallyLoc) {
          var i = o;
          break;
        }
      }
      i && ("break" === t || "continue" === t) && i.tryLoc <= e && e <= i.finallyLoc && (i = null);
      var a = i ? i.completion : {};
      return a.type = t, a.arg = e, i ? (this.method = "next", this.next = i.finallyLoc, y) : this.complete(a);
    },
    complete: function (t, e) {
      if ("throw" === t.type) throw t.arg;
      return "break" === t.type || "continue" === t.type ? this.next = t.arg : "return" === t.type ? (this.rval = this.arg = t.arg, this.method = "return", this.next = "end") : "normal" === t.type && e && (this.next = e), y;
    },
    finish: function (t) {
      for (var e = this.tryEntries.length - 1; e >= 0; --e) {
        var r = this.tryEntries[e];
        if (r.finallyLoc === t) return this.complete(r.completion, r.afterLoc), resetTryEntry(r), y;
      }
    },
    catch: function (t) {
      for (var e = this.tryEntries.length - 1; e >= 0; --e) {
        var r = this.tryEntries[e];
        if (r.tryLoc === t) {
          var n = r.completion;
          if ("throw" === n.type) {
            var o = n.arg;
            resetTryEntry(r);
          }
          return o;
        }
      }
      throw new Error("illegal catch attempt");
    },
    delegateYield: function (e, r, n) {
      return this.delegate = {
        iterator: values(e),
        resultName: r,
        nextLoc: n
      }, "next" === this.method && (this.arg = t), y;
    }
  }, e;
}
function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) {
  try {
    var info = gen[key](arg);
    var value = info.value;
  } catch (error) {
    reject(error);
    return;
  }
  if (info.done) {
    resolve(value);
  } else {
    Promise.resolve(value).then(_next, _throw);
  }
}
function _asyncToGenerator(fn) {
  return function () {
    var self = this,
      args = arguments;
    return new Promise(function (resolve, reject) {
      var gen = fn.apply(self, args);
      function _next(value) {
        asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value);
      }
      function _throw(err) {
        asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err);
      }
      _next(undefined);
    });
  };
}
function _defineProperties(target, props) {
  for (var i = 0; i < props.length; i++) {
    var descriptor = props[i];
    descriptor.enumerable = descriptor.enumerable || false;
    descriptor.configurable = true;
    if ("value" in descriptor) descriptor.writable = true;
    Object.defineProperty(target, _toPropertyKey(descriptor.key), descriptor);
  }
}
function _createClass(Constructor, protoProps, staticProps) {
  if (protoProps) _defineProperties(Constructor.prototype, protoProps);
  if (staticProps) _defineProperties(Constructor, staticProps);
  Object.defineProperty(Constructor, "prototype", {
    writable: false
  });
  return Constructor;
}
function _extends() {
  _extends = Object.assign ? Object.assign.bind() : function (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];
      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  };
  return _extends.apply(this, arguments);
}
function _inheritsLoose(subClass, superClass) {
  subClass.prototype = Object.create(superClass.prototype);
  subClass.prototype.constructor = subClass;
  _setPrototypeOf(subClass, superClass);
}
function _getPrototypeOf(o) {
  _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function _getPrototypeOf(o) {
    return o.__proto__ || Object.getPrototypeOf(o);
  };
  return _getPrototypeOf(o);
}
function _setPrototypeOf(o, p) {
  _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) {
    o.__proto__ = p;
    return o;
  };
  return _setPrototypeOf(o, p);
}
function _isNativeReflectConstruct() {
  if (typeof Reflect === "undefined" || !Reflect.construct) return false;
  if (Reflect.construct.sham) return false;
  if (typeof Proxy === "function") return true;
  try {
    Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {}));
    return true;
  } catch (e) {
    return false;
  }
}
function _construct(Parent, args, Class) {
  if (_isNativeReflectConstruct()) {
    _construct = Reflect.construct.bind();
  } else {
    _construct = function _construct(Parent, args, Class) {
      var a = [null];
      a.push.apply(a, args);
      var Constructor = Function.bind.apply(Parent, a);
      var instance = new Constructor();
      if (Class) _setPrototypeOf(instance, Class.prototype);
      return instance;
    };
  }
  return _construct.apply(null, arguments);
}
function _isNativeFunction(fn) {
  return Function.toString.call(fn).indexOf("[native code]") !== -1;
}
function _wrapNativeSuper(Class) {
  var _cache = typeof Map === "function" ? new Map() : undefined;
  _wrapNativeSuper = function _wrapNativeSuper(Class) {
    if (Class === null || !_isNativeFunction(Class)) return Class;
    if (typeof Class !== "function") {
      throw new TypeError("Super expression must either be null or a function");
    }
    if (typeof _cache !== "undefined") {
      if (_cache.has(Class)) return _cache.get(Class);
      _cache.set(Class, Wrapper);
    }
    function Wrapper() {
      return _construct(Class, arguments, _getPrototypeOf(this).constructor);
    }
    Wrapper.prototype = Object.create(Class.prototype, {
      constructor: {
        value: Wrapper,
        enumerable: false,
        writable: true,
        configurable: true
      }
    });
    return _setPrototypeOf(Wrapper, Class);
  };
  return _wrapNativeSuper(Class);
}
function _objectWithoutPropertiesLoose(source, excluded) {
  if (source == null) return {};
  var target = {};
  var sourceKeys = Object.keys(source);
  var key, i;
  for (i = 0; i < sourceKeys.length; i++) {
    key = sourceKeys[i];
    if (excluded.indexOf(key) >= 0) continue;
    target[key] = source[key];
  }
  return target;
}
function _unsupportedIterableToArray(o, minLen) {
  if (!o) return;
  if (typeof o === "string") return _arrayLikeToArray(o, minLen);
  var n = Object.prototype.toString.call(o).slice(8, -1);
  if (n === "Object" && o.constructor) n = o.constructor.name;
  if (n === "Map" || n === "Set") return Array.from(o);
  if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen);
}
function _arrayLikeToArray(arr, len) {
  if (len == null || len > arr.length) len = arr.length;
  for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i];
  return arr2;
}
function _createForOfIteratorHelperLoose(o, allowArrayLike) {
  var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"];
  if (it) return (it = it.call(o)).next.bind(it);
  if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") {
    if (it) o = it;
    var i = 0;
    return function () {
      if (i >= o.length) return {
        done: true
      };
      return {
        done: false,
        value: o[i++]
      };
    };
  }
  throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function _toPrimitive(input, hint) {
  if (typeof input !== "object" || input === null) return input;
  var prim = input[Symbol.toPrimitive];
  if (prim !== undefined) {
    var res = prim.call(input, hint || "default");
    if (typeof res !== "object") return res;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (hint === "string" ? String : Number)(input);
}
function _toPropertyKey(arg) {
  var key = _toPrimitive(arg, "string");
  return typeof key === "symbol" ? key : String(key);
}

// constants used internally but not expected to be used externally
var NEGATIVE_ONE = /*#__PURE__*/JSBI.BigInt(-1);
var ZERO = /*#__PURE__*/JSBI.BigInt(0);
var ONE = /*#__PURE__*/JSBI.BigInt(1);
// used in liquidity amount math
var Q96 = /*#__PURE__*/JSBI.exponentiate( /*#__PURE__*/JSBI.BigInt(2), /*#__PURE__*/JSBI.BigInt(96));
var Q192 = /*#__PURE__*/JSBI.exponentiate(Q96, /*#__PURE__*/JSBI.BigInt(2));
var MaxUint256 = /*#__PURE__*/JSBI.BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff');

var ChainId = {
  BaseSepolia: 84532
};

var ADDRESS_ZERO = '0x0000000000000000000000000000000000000000';
var INITIAL_POOL_FEE = 100;
var DEFAULT_TICK_SPACING = 60;

var _POOL_DEPLOYER_ADDRES, _POOL_INIT_CODE_HASH;
var POOL_DEPLOYER_ADDRESSES = (_POOL_DEPLOYER_ADDRES = {}, _POOL_DEPLOYER_ADDRES[ChainId.BaseSepolia] = '0xA064Bcb79F27213b6e39dC4a2E3b977e97489BC9', _POOL_DEPLOYER_ADDRES);
var POOL_INIT_CODE_HASH = (_POOL_INIT_CODE_HASH = {}, _POOL_INIT_CODE_HASH[ChainId.BaseSepolia] = '0x62441ebe4e4315cf3d49d5957f94d66b253dbabe7006f34ad7f70947e60bf15c', _POOL_INIT_CODE_HASH);

/**
 * A currency is any fungible financial instrument, including Ether, all ERC20 tokens, and other chain-native currencies
 */
var AbstractCurrency =
/**
 * Constructs an instance of the base class `BaseCurrency`.
 * @param chainId the chain ID on which this currency resides
 * @param decimals decimals of the currency
 * @param symbol symbol of the currency
 * @param name of the currency
 */
function AbstractCurrency(chainId, decimals, symbol, name) {
  !Number.isSafeInteger(chainId) ? process.env.NODE_ENV !== "production" ? invariant(false, 'CHAIN_ID') : invariant(false) : void 0;
  !(decimals >= 0 && decimals < 255 && Number.isInteger(decimals)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'DECIMALS') : invariant(false) : void 0;
  this.chainId = chainId;
  this.decimals = decimals;
  this.symbol = symbol;
  this.name = name;
};

function validateAndParseAddress(address) {
  try {
    return getAddress(address);
  } catch (error) {
    throw new Error(address + " is not a valid address.");
  }
}

/**
 * Represents an ERC20 token with a unique address and some metadata.
 */
var Token = /*#__PURE__*/function (_AbstractCurrency) {
  _inheritsLoose(Token, _AbstractCurrency);
  function Token(chainId, address, decimals, symbol, name) {
    var _this;
    _this = _AbstractCurrency.call(this, chainId, decimals, symbol, name) || this;
    _this.isNative = false;
    _this.isBoosted = false;
    _this.isToken = true;
    _this.chainId = chainId;
    _this.address = validateAndParseAddress(address);
    return _this;
  }
  /**
   * Returns true if the two tokens are equivalent, i.e. have the same chainId and address.
   * @param other other token to compare
   */
  var _proto = Token.prototype;
  _proto.equals = function equals(other) {
    return other.isToken && this.chainId === other.chainId && this.address === other.address;
  }
  /**
   * Returns true if the address of this token sorts before the address of the other token
   * @param other other token to compare
   * @throws if the tokens have the same address
   * @throws if the tokens are on different chains
   */;
  _proto.sortsBefore = function sortsBefore(other) {
    !(this.chainId === other.chainId) ? process.env.NODE_ENV !== "production" ? invariant(false, 'CHAIN_IDS') : invariant(false) : void 0;
    !(this.address !== other.address) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ADDRESSES') : invariant(false) : void 0;
    return this.address.toLowerCase() < other.address.toLowerCase();
  }
  /**
   * Return this token, which does not need to be wrapped
   */;
  _createClass(Token, [{
    key: "wrapped",
    get: function get() {
      return this;
    }
  }]);
  return Token;
}(AbstractCurrency);
/**
 * Compares two currencies for equality
 */
function currencyEquals(currencyA, currencyB) {
  if (currencyA instanceof Token && currencyB instanceof Token) {
    return currencyA.equals(currencyB);
  } else if (currencyA instanceof Token) {
    return false;
  } else if (currencyB instanceof Token) {
    return false;
  } else {
    return currencyA === currencyB;
  }
}

var _WNATIVE;
/**
 * Known WETH9 implementation addresses, used in our implementation of Ether#wrapped
 */
var WNATIVE = (_WNATIVE = {}, _WNATIVE[ChainId.BaseSepolia] = /*#__PURE__*/new Token(ChainId.BaseSepolia, '0x4200000000000000000000000000000000000006', 18, 'WETH', 'Wrapped ETH'), _WNATIVE);

/**
 * Computes a pool address
 * @param poolDeployer The Algebra Pool Deployer address
 * @param tokenA The first token of the pair, irrespective of sort order
 * @param tokenB The second token of the pair, irrespective of sort order
 * @param initCodeHashManualOverride The initial code hash override
 * @returns The pool address
 */
function computePoolAddress(_ref) {
  var tokenA = _ref.tokenA,
    tokenB = _ref.tokenB,
    initCodeHashManualOverride = _ref.initCodeHashManualOverride,
    poolDeployer = _ref.poolDeployer;
  var _ref2 = tokenA.sortsBefore(tokenB) ? [tokenA, tokenB] : [tokenB, tokenA],
    token0 = _ref2[0],
    token1 = _ref2[1];
  return getCreate2Address(poolDeployer != null ? poolDeployer : POOL_DEPLOYER_ADDRESSES[tokenA.chainId], keccak256(['bytes'], [defaultAbiCoder.encode(['address', 'address'], [token0.address, token1.address])]), initCodeHashManualOverride != null ? initCodeHashManualOverride : POOL_INIT_CODE_HASH[tokenA.chainId]);
}
function computeCustomPoolAddress(_ref3) {
  var tokenA = _ref3.tokenA,
    tokenB = _ref3.tokenB,
    customPoolDeployer = _ref3.customPoolDeployer,
    initCodeHashManualOverride = _ref3.initCodeHashManualOverride,
    mainPoolDeployer = _ref3.mainPoolDeployer;
  var _ref4 = tokenA.sortsBefore(tokenB) ? [tokenA, tokenB] : [tokenB, tokenA],
    token0 = _ref4[0],
    token1 = _ref4[1];
  return getCreate2Address(mainPoolDeployer != null ? mainPoolDeployer : POOL_DEPLOYER_ADDRESSES[tokenA.chainId], keccak256(['bytes'], [defaultAbiCoder.encode(['address', 'address', 'address'], [customPoolDeployer, token0.address, token1.address])]), initCodeHashManualOverride != null ? initCodeHashManualOverride : POOL_INIT_CODE_HASH[tokenA.chainId]);
}
function computePoolAddressZkSync(_ref5) {
  var poolDeployer = _ref5.poolDeployer,
    tokenA = _ref5.tokenA,
    tokenB = _ref5.tokenB,
    initCodeHashManualOverride = _ref5.initCodeHashManualOverride;
  var _ref6 = tokenA.sortsBefore(tokenB) ? [tokenA, tokenB] : [tokenB, tokenA],
    token0 = _ref6[0],
    token1 = _ref6[1]; // does safety checks
  return getCreate2AddressZk(poolDeployer != null ? poolDeployer : POOL_DEPLOYER_ADDRESSES[tokenA.chainId], keccak256(['bytes'], [defaultAbiCoder.encode(['address', 'address'], [token0.address, token1.address])]), initCodeHashManualOverride != null ? initCodeHashManualOverride : POOL_INIT_CODE_HASH[tokenA.chainId]);
}
function getCreate2AddressZk(from, salt, initCodeHash) {
  var prefix = keccak256$1(toUtf8Bytes('zksyncCreate2'));
  var addressBytes = keccak256$1(concat([prefix, zeroPad(from, 32), salt, initCodeHash, '0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'])).slice(26);
  return getAddress(addressBytes);
}

var LiquidityMath = /*#__PURE__*/function () {
  function LiquidityMath() {}
  /**
   * Cannot be constructed.
   */
  LiquidityMath.addDelta = function addDelta(x, y) {
    if (JSBI.lessThan(y, ZERO)) {
      return JSBI.subtract(x, JSBI.multiply(y, NEGATIVE_ONE));
    } else {
      return JSBI.add(x, y);
    }
  };
  return LiquidityMath;
}();

var FullMath = /*#__PURE__*/function () {
  function FullMath() {}
  /**
   * Cannot be constructed.
   */
  FullMath.mulDivRoundingUp = function mulDivRoundingUp(a, b, denominator) {
    var product = JSBI.multiply(a, b);
    var result = JSBI.divide(product, denominator);
    if (JSBI.notEqual(JSBI.remainder(product, denominator), ZERO)) result = JSBI.add(result, ONE);
    return result;
  };
  return FullMath;
}();

var MaxUint160 = /*#__PURE__*/JSBI.subtract( /*#__PURE__*/JSBI.exponentiate( /*#__PURE__*/JSBI.BigInt(2), /*#__PURE__*/JSBI.BigInt(160)), ONE);
function multiplyIn256(x, y) {
  var product = JSBI.multiply(x, y);
  return JSBI.bitwiseAnd(product, MaxUint256);
}
function addIn256(x, y) {
  var sum = JSBI.add(x, y);
  return JSBI.bitwiseAnd(sum, MaxUint256);
}
var SqrtPriceMath = /*#__PURE__*/function () {
  function SqrtPriceMath() {}
  /**
   * Cannot be constructed.
   */
  SqrtPriceMath.getAmount0Delta = function getAmount0Delta(sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp) {
    if (JSBI.greaterThan(sqrtRatioAX96, sqrtRatioBX96)) {
      var _ref = [sqrtRatioBX96, sqrtRatioAX96];
      sqrtRatioAX96 = _ref[0];
      sqrtRatioBX96 = _ref[1];
    }
    var numerator1 = JSBI.leftShift(liquidity, JSBI.BigInt(96));
    var numerator2 = JSBI.subtract(sqrtRatioBX96, sqrtRatioAX96);
    return roundUp ? FullMath.mulDivRoundingUp(FullMath.mulDivRoundingUp(numerator1, numerator2, sqrtRatioBX96), ONE, sqrtRatioAX96) : JSBI.divide(JSBI.divide(JSBI.multiply(numerator1, numerator2), sqrtRatioBX96), sqrtRatioAX96);
  };
  SqrtPriceMath.getAmount1Delta = function getAmount1Delta(sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp) {
    if (JSBI.greaterThan(sqrtRatioAX96, sqrtRatioBX96)) {
      var _ref2 = [sqrtRatioBX96, sqrtRatioAX96];
      sqrtRatioAX96 = _ref2[0];
      sqrtRatioBX96 = _ref2[1];
    }
    return roundUp ? FullMath.mulDivRoundingUp(liquidity, JSBI.subtract(sqrtRatioBX96, sqrtRatioAX96), Q96) : JSBI.divide(JSBI.multiply(liquidity, JSBI.subtract(sqrtRatioBX96, sqrtRatioAX96)), Q96);
  };
  SqrtPriceMath.getNextSqrtPriceFromInput = function getNextSqrtPriceFromInput(sqrtPX96, liquidity, amountIn, zeroForOne) {
    !JSBI.greaterThan(sqrtPX96, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
    !JSBI.greaterThan(liquidity, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
    return zeroForOne ? this.getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountIn, true) : this.getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountIn, true);
  };
  SqrtPriceMath.getNextSqrtPriceFromOutput = function getNextSqrtPriceFromOutput(sqrtPX96, liquidity, amountOut, zeroForOne) {
    !JSBI.greaterThan(sqrtPX96, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
    !JSBI.greaterThan(liquidity, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
    return zeroForOne ? this.getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountOut, false) : this.getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountOut, false);
  };
  SqrtPriceMath.getNextSqrtPriceFromAmount0RoundingUp = function getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amount, add) {
    if (JSBI.equal(amount, ZERO)) return sqrtPX96;
    var numerator1 = JSBI.leftShift(liquidity, JSBI.BigInt(96));
    if (add) {
      var product = multiplyIn256(amount, sqrtPX96);
      if (JSBI.equal(JSBI.divide(product, amount), sqrtPX96)) {
        var denominator = addIn256(numerator1, product);
        if (JSBI.greaterThanOrEqual(denominator, numerator1)) {
          return FullMath.mulDivRoundingUp(numerator1, sqrtPX96, denominator);
        }
      }
      return FullMath.mulDivRoundingUp(numerator1, ONE, JSBI.add(JSBI.divide(numerator1, sqrtPX96), amount));
    } else {
      var _product = multiplyIn256(amount, sqrtPX96);
      !JSBI.equal(JSBI.divide(_product, amount), sqrtPX96) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
      !JSBI.greaterThan(numerator1, _product) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
      var _denominator = JSBI.subtract(numerator1, _product);
      return FullMath.mulDivRoundingUp(numerator1, sqrtPX96, _denominator);
    }
  };
  SqrtPriceMath.getNextSqrtPriceFromAmount1RoundingDown = function getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amount, add) {
    if (add) {
      var quotient = JSBI.lessThanOrEqual(amount, MaxUint160) ? JSBI.divide(JSBI.leftShift(amount, JSBI.BigInt(96)), liquidity) : JSBI.divide(JSBI.multiply(amount, Q96), liquidity);
      return JSBI.add(sqrtPX96, quotient);
    } else {
      var _quotient = FullMath.mulDivRoundingUp(amount, Q96, liquidity);
      !JSBI.greaterThan(sqrtPX96, _quotient) ? process.env.NODE_ENV !== "production" ? invariant(false) : invariant(false) : void 0;
      return JSBI.subtract(sqrtPX96, _quotient);
    }
  };
  return SqrtPriceMath;
}();

var MAX_FEE = /*#__PURE__*/JSBI.exponentiate( /*#__PURE__*/JSBI.BigInt(10), /*#__PURE__*/JSBI.BigInt(6));
var SwapMath = /*#__PURE__*/function () {
  function SwapMath() {}
  /**
   * Cannot be constructed.
   */
  SwapMath.computeSwapStep = function computeSwapStep(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, amountRemaining, feePips) {
    var returnValues = {};
    var zeroForOne = JSBI.greaterThanOrEqual(sqrtRatioCurrentX96, sqrtRatioTargetX96);
    var exactIn = JSBI.greaterThanOrEqual(amountRemaining, ZERO);
    if (exactIn) {
      var amountRemainingLessFee = JSBI.divide(JSBI.multiply(amountRemaining, JSBI.subtract(MAX_FEE, JSBI.BigInt(feePips))), MAX_FEE);
      returnValues.amountIn = zeroForOne ? SqrtPriceMath.getAmount0Delta(sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, true) : SqrtPriceMath.getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, true);
      if (JSBI.greaterThanOrEqual(amountRemainingLessFee, returnValues.amountIn)) {
        returnValues.sqrtRatioNextX96 = sqrtRatioTargetX96;
      } else {
        returnValues.sqrtRatioNextX96 = SqrtPriceMath.getNextSqrtPriceFromInput(sqrtRatioCurrentX96, liquidity, amountRemainingLessFee, zeroForOne);
      }
    } else {
      returnValues.amountOut = zeroForOne ? SqrtPriceMath.getAmount1Delta(sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, false) : SqrtPriceMath.getAmount0Delta(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, false);
      if (JSBI.greaterThanOrEqual(JSBI.multiply(amountRemaining, NEGATIVE_ONE), returnValues.amountOut)) {
        returnValues.sqrtRatioNextX96 = sqrtRatioTargetX96;
      } else {
        returnValues.sqrtRatioNextX96 = SqrtPriceMath.getNextSqrtPriceFromOutput(sqrtRatioCurrentX96, liquidity, JSBI.multiply(amountRemaining, NEGATIVE_ONE), zeroForOne);
      }
    }
    var max = JSBI.equal(sqrtRatioTargetX96, returnValues.sqrtRatioNextX96);
    if (zeroForOne) {
      returnValues.amountIn = max && exactIn ? returnValues.amountIn : SqrtPriceMath.getAmount0Delta(returnValues.sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, true);
      returnValues.amountOut = max && !exactIn ? returnValues.amountOut : SqrtPriceMath.getAmount1Delta(returnValues.sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, false);
    } else {
      returnValues.amountIn = max && exactIn ? returnValues.amountIn : SqrtPriceMath.getAmount1Delta(sqrtRatioCurrentX96, returnValues.sqrtRatioNextX96, liquidity, true);
      returnValues.amountOut = max && !exactIn ? returnValues.amountOut : SqrtPriceMath.getAmount0Delta(sqrtRatioCurrentX96, returnValues.sqrtRatioNextX96, liquidity, false);
    }
    if (!exactIn && JSBI.greaterThan(returnValues.amountOut, JSBI.multiply(amountRemaining, NEGATIVE_ONE))) {
      returnValues.amountOut = JSBI.multiply(amountRemaining, NEGATIVE_ONE);
    }
    if (exactIn && JSBI.notEqual(returnValues.sqrtRatioNextX96, sqrtRatioTargetX96)) {
      // we didn't reach the target, so take the remainder of the maximum input as fee
      returnValues.feeAmount = JSBI.subtract(amountRemaining, returnValues.amountIn);
    } else {
      returnValues.feeAmount = FullMath.mulDivRoundingUp(returnValues.amountIn, JSBI.BigInt(feePips), JSBI.subtract(MAX_FEE, JSBI.BigInt(feePips)));
    }
    return [returnValues.sqrtRatioNextX96, returnValues.amountIn, returnValues.amountOut, returnValues.feeAmount];
  };
  return SwapMath;
}();

var TWO = /*#__PURE__*/JSBI.BigInt(2);
var POWERS_OF_2 = /*#__PURE__*/[128, 64, 32, 16, 8, 4, 2, 1].map(function (pow) {
  return [pow, JSBI.exponentiate(TWO, JSBI.BigInt(pow))];
});
function mostSignificantBit(x) {
  !JSBI.greaterThan(x, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ZERO') : invariant(false) : void 0;
  !JSBI.lessThanOrEqual(x, MaxUint256) ? process.env.NODE_ENV !== "production" ? invariant(false, 'MAX') : invariant(false) : void 0;
  var msb = 0;
  for (var _iterator = _createForOfIteratorHelperLoose(POWERS_OF_2), _step; !(_step = _iterator()).done;) {
    var _step$value = _step.value,
      power = _step$value[0],
      min = _step$value[1];
    if (JSBI.greaterThanOrEqual(x, min)) {
      x = JSBI.signedRightShift(x, JSBI.BigInt(power));
      msb += power;
    }
  }
  return msb;
}

function mulShift(val, mulBy) {
  return JSBI.signedRightShift(JSBI.multiply(val, JSBI.BigInt(mulBy)), JSBI.BigInt(128));
}
var Q32 = /*#__PURE__*/JSBI.exponentiate( /*#__PURE__*/JSBI.BigInt(2), /*#__PURE__*/JSBI.BigInt(32));
var TickMath = /*#__PURE__*/function () {
  function TickMath() {}
  /**
   * Returns the sqrt ratio as a Q64.96 for the given tick. The sqrt ratio is computed as sqrt(1.0001)^tick
   * @param tick the tick for which to compute the sqrt ratio
   */
  TickMath.getSqrtRatioAtTick = function getSqrtRatioAtTick(tick) {
    !(tick >= TickMath.MIN_TICK && tick <= TickMath.MAX_TICK && Number.isInteger(tick)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK') : invariant(false) : void 0;
    var absTick = tick < 0 ? tick * -1 : tick;
    var ratio = (absTick & 0x1) != 0 ? JSBI.BigInt('0xfffcb933bd6fad37aa2d162d1a594001') : JSBI.BigInt('0x100000000000000000000000000000000');
    if ((absTick & 0x2) != 0) ratio = mulShift(ratio, '0xfff97272373d413259a46990580e213a');
    if ((absTick & 0x4) != 0) ratio = mulShift(ratio, '0xfff2e50f5f656932ef12357cf3c7fdcc');
    if ((absTick & 0x8) != 0) ratio = mulShift(ratio, '0xffe5caca7e10e4e61c3624eaa0941cd0');
    if ((absTick & 0x10) != 0) ratio = mulShift(ratio, '0xffcb9843d60f6159c9db58835c926644');
    if ((absTick & 0x20) != 0) ratio = mulShift(ratio, '0xff973b41fa98c081472e6896dfb254c0');
    if ((absTick & 0x40) != 0) ratio = mulShift(ratio, '0xff2ea16466c96a3843ec78b326b52861');
    if ((absTick & 0x80) != 0) ratio = mulShift(ratio, '0xfe5dee046a99a2a811c461f1969c3053');
    if ((absTick & 0x100) != 0) ratio = mulShift(ratio, '0xfcbe86c7900a88aedcffc83b479aa3a4');
    if ((absTick & 0x200) != 0) ratio = mulShift(ratio, '0xf987a7253ac413176f2b074cf7815e54');
    if ((absTick & 0x400) != 0) ratio = mulShift(ratio, '0xf3392b0822b70005940c7a398e4b70f3');
    if ((absTick & 0x800) != 0) ratio = mulShift(ratio, '0xe7159475a2c29b7443b29c7fa6e889d9');
    if ((absTick & 0x1000) != 0) ratio = mulShift(ratio, '0xd097f3bdfd2022b8845ad8f792aa5825');
    if ((absTick & 0x2000) != 0) ratio = mulShift(ratio, '0xa9f746462d870fdf8a65dc1f90e061e5');
    if ((absTick & 0x4000) != 0) ratio = mulShift(ratio, '0x70d869a156d2a1b890bb3df62baf32f7');
    if ((absTick & 0x8000) != 0) ratio = mulShift(ratio, '0x31be135f97d08fd981231505542fcfa6');
    if ((absTick & 0x10000) != 0) ratio = mulShift(ratio, '0x9aa508b5b7a84e1c677de54f3e99bc9');
    if ((absTick & 0x20000) != 0) ratio = mulShift(ratio, '0x5d6af8dedb81196699c329225ee604');
    if ((absTick & 0x40000) != 0) ratio = mulShift(ratio, '0x2216e584f5fa1ea926041bedfe98');
    if ((absTick & 0x80000) != 0) ratio = mulShift(ratio, '0x48a170391f7dc42444e8fa2');
    if (tick > 0) ratio = JSBI.divide(MaxUint256, ratio);
    // back to Q96
    return JSBI.greaterThan(JSBI.remainder(ratio, Q32), ZERO) ? JSBI.add(JSBI.divide(ratio, Q32), ONE) : JSBI.divide(ratio, Q32);
  }
  /**
   * Returns the tick corresponding to a given sqrt ratio, s.t. #getSqrtRatioAtTick(tick) <= sqrtRatioX96
   * and #getSqrtRatioAtTick(tick + 1) > sqrtRatioX96
   * @param sqrtRatioX96 the sqrt ratio as a Q64.96 for which to compute the tick
   */;
  TickMath.getTickAtSqrtRatio = function getTickAtSqrtRatio(sqrtRatioX96) {
    !(JSBI.greaterThanOrEqual(sqrtRatioX96, TickMath.MIN_SQRT_RATIO) && JSBI.lessThan(sqrtRatioX96, TickMath.MAX_SQRT_RATIO)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'SQRT_RATIO') : invariant(false) : void 0;
    var sqrtRatioX128 = JSBI.leftShift(sqrtRatioX96, JSBI.BigInt(32));
    var msb = mostSignificantBit(sqrtRatioX128);
    var r;
    if (JSBI.greaterThanOrEqual(JSBI.BigInt(msb), JSBI.BigInt(128))) {
      r = JSBI.signedRightShift(sqrtRatioX128, JSBI.BigInt(msb - 127));
    } else {
      r = JSBI.leftShift(sqrtRatioX128, JSBI.BigInt(127 - msb));
    }
    var log_2 = JSBI.leftShift(JSBI.subtract(JSBI.BigInt(msb), JSBI.BigInt(128)), JSBI.BigInt(64));
    for (var i = 0; i < 14; i++) {
      r = JSBI.signedRightShift(JSBI.multiply(r, r), JSBI.BigInt(127));
      var f = JSBI.signedRightShift(r, JSBI.BigInt(128));
      log_2 = JSBI.bitwiseOr(log_2, JSBI.leftShift(f, JSBI.BigInt(63 - i)));
      r = JSBI.signedRightShift(r, f);
    }
    var log_sqrt10001 = JSBI.multiply(log_2, JSBI.BigInt('255738958999603826347141'));
    var tickLow = JSBI.toNumber(JSBI.signedRightShift(JSBI.subtract(log_sqrt10001, JSBI.BigInt('3402992956809132418596140100660247210')), JSBI.BigInt(128)));
    var tickHigh = JSBI.toNumber(JSBI.signedRightShift(JSBI.add(log_sqrt10001, JSBI.BigInt('291339464771989622907027621153398088495')), JSBI.BigInt(128)));
    return tickLow === tickHigh ? tickLow : JSBI.lessThanOrEqual(TickMath.getSqrtRatioAtTick(tickHigh), sqrtRatioX96) ? tickHigh : tickLow;
  };
  return TickMath;
}();
/**
 * Cannot be constructed.
 */
/**
 * The minimum tick that can be used on any pool.
 */
TickMath.MIN_TICK = -887272;
/**
 * The maximum tick that can be used on any pool.
 */
TickMath.MAX_TICK = -TickMath.MIN_TICK;
/**
 * The sqrt ratio corresponding to the minimum tick that could be used on any pool.
 */
TickMath.MIN_SQRT_RATIO = /*#__PURE__*/JSBI.BigInt('4295128739');
/**
 * The sqrt ratio corresponding to the maximum tick that could be used on any pool.
 */
TickMath.MAX_SQRT_RATIO = /*#__PURE__*/JSBI.BigInt('1461446703485210103287273052203988822378723970342');

/**
 * This tick data provider does not know how to fetch any tick data. It throws whenever it is required. Useful if you
 * do not need to load tick data for your use case.
 */
var NoTickDataProvider = /*#__PURE__*/function () {
  function NoTickDataProvider() {}
  var _proto = NoTickDataProvider.prototype;
  _proto.getTick = /*#__PURE__*/function () {
    var _getTick = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee(_tick) {
      return _regeneratorRuntime().wrap(function _callee$(_context) {
        while (1) switch (_context.prev = _context.next) {
          case 0:
            throw new Error(NoTickDataProvider.ERROR_MESSAGE);
          case 1:
          case "end":
            return _context.stop();
        }
      }, _callee);
    }));
    function getTick(_x) {
      return _getTick.apply(this, arguments);
    }
    return getTick;
  }();
  _proto.nextInitializedTickWithinOneWord = /*#__PURE__*/function () {
    var _nextInitializedTickWithinOneWord = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee2(_tick, _lte, _tickSpacing) {
      return _regeneratorRuntime().wrap(function _callee2$(_context2) {
        while (1) switch (_context2.prev = _context2.next) {
          case 0:
            throw new Error(NoTickDataProvider.ERROR_MESSAGE);
          case 1:
          case "end":
            return _context2.stop();
        }
      }, _callee2);
    }));
    function nextInitializedTickWithinOneWord(_x2, _x3, _x4) {
      return _nextInitializedTickWithinOneWord.apply(this, arguments);
    }
    return nextInitializedTickWithinOneWord;
  }();
  return NoTickDataProvider;
}();
NoTickDataProvider.ERROR_MESSAGE = 'No tick data provider was given';

/**
 * Determines if a tick list is sorted
 * @param list The tick list
 * @param comparator The comparator
 * @returns true if sorted
 */
function isSorted(list, comparator) {
  for (var i = 0; i < list.length - 1; i++) {
    if (comparator(list[i], list[i + 1]) > 0) {
      return false;
    }
  }
  return true;
}

function tickComparator(a, b) {
  return a.index - b.index;
}
/**
 * Utility methods for interacting with sorted lists of ticks
 */
var TickList = /*#__PURE__*/function () {
  function TickList() {}
  /**
   * Cannot be constructed
   */
  TickList.validateList = function validateList(ticks, tickSpacing) {
    !(tickSpacing > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_SPACING_NONZERO') : invariant(false) : void 0;
    // ensure ticks are spaced appropriately
    !ticks.every(function (_ref) {
      var index = _ref.index;
      return index % tickSpacing === 0;
    }) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_SPACING') : invariant(false) : void 0;
    // ensure tick liquidity deltas sum to 0
    !JSBI.equal(ticks.reduce(function (accumulator, _ref2) {
      var liquidityNet = _ref2.liquidityNet;
      return JSBI.add(accumulator, liquidityNet);
    }, ZERO), ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ZERO_NET') : invariant(false) : void 0;
    !isSorted(ticks, tickComparator) ? process.env.NODE_ENV !== "production" ? invariant(false, 'SORTED') : invariant(false) : void 0;
  };
  TickList.isBelowSmallest = function isBelowSmallest(ticks, tick) {
    !(ticks.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'LENGTH') : invariant(false) : void 0;
    return tick < ticks[0].index;
  };
  TickList.isAtOrAboveLargest = function isAtOrAboveLargest(ticks, tick) {
    !(ticks.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'LENGTH') : invariant(false) : void 0;
    return tick >= ticks[ticks.length - 1].index;
  };
  TickList.getTick = function getTick(ticks, index) {
    var tick = ticks[this.binarySearch(ticks, index)];
    !(tick.index === index) ? process.env.NODE_ENV !== "production" ? invariant(false, 'NOT_CONTAINED') : invariant(false) : void 0;
    return tick;
  };
  TickList.nextInitializedTick = function nextInitializedTick(ticks, tick, lte) {
    if (lte) {
      !!TickList.isBelowSmallest(ticks, tick) ? process.env.NODE_ENV !== "production" ? invariant(false, 'BELOW_SMALLEST') : invariant(false) : void 0;
      if (TickList.isAtOrAboveLargest(ticks, tick)) {
        return ticks[ticks.length - 1];
      }
      var index = this.binarySearch(ticks, tick);
      return ticks[index];
    } else {
      !!this.isAtOrAboveLargest(ticks, tick) ? process.env.NODE_ENV !== "production" ? invariant(false, 'AT_OR_ABOVE_LARGEST') : invariant(false) : void 0;
      if (this.isBelowSmallest(ticks, tick)) {
        return ticks[0];
      }
      var _index = this.binarySearch(ticks, tick);
      return ticks[_index + 1];
    }
  };
  TickList.nextInitializedTickWithinOneWord = function nextInitializedTickWithinOneWord(ticks, tick, lte, tickSpacing) {
    var compressed = Math.floor(tick / tickSpacing); // matches rounding in the code
    if (lte) {
      var wordPos = compressed >> 8;
      var minimum = (wordPos << 8) * tickSpacing;
      if (TickList.isBelowSmallest(ticks, tick)) {
        return [minimum, false];
      }
      var index = TickList.nextInitializedTick(ticks, tick, lte).index;
      var nextInitializedTick = Math.max(minimum, index);
      return [nextInitializedTick, nextInitializedTick === index];
    } else {
      var _wordPos = compressed + 1 >> 8;
      var maximum = (_wordPos + 1 << 8) * tickSpacing - 1;
      if (this.isAtOrAboveLargest(ticks, tick)) {
        return [maximum, false];
      }
      var _index2 = this.nextInitializedTick(ticks, tick, lte).index;
      var _nextInitializedTick = Math.min(maximum, _index2);
      return [_nextInitializedTick, _nextInitializedTick === _index2];
    }
  }
  /**
   * Finds the largest tick in the list of ticks that is less than or equal to tick
   * @param ticks list of ticks
   * @param tick tick to find the largest tick that is less than or equal to tick
   * @private
   */;
  TickList.binarySearch = function binarySearch(ticks, tick) {
    !!this.isBelowSmallest(ticks, tick) ? process.env.NODE_ENV !== "production" ? invariant(false, 'BELOW_SMALLEST') : invariant(false) : void 0;
    var l = 0;
    var r = ticks.length - 1;
    var i;
    while (true) {
      i = Math.floor((l + r) / 2);
      if (ticks[i].index <= tick && (i === ticks.length - 1 || ticks[i + 1].index > tick)) {
        return i;
      }
      if (ticks[i].index < tick) {
        l = i + 1;
      } else {
        r = i - 1;
      }
    }
  };
  return TickList;
}();

/**
 * Converts a big int to a hex string
 * @param bigintIsh
 * @returns The hex encoded calldata
 */
function toHex(bigintIsh) {
  var bigInt = JSBI.BigInt(bigintIsh);
  var hex = bigInt.toString(16);
  if (hex.length % 2 !== 0) {
    hex = "0" + hex;
  }
  return "0x" + hex;
}

/**
 * Converts a route to a hex encoded path
 * @param route the v3 path to convert to an encoded path
 * @param exactOutput whether the route should be encoded in reverse, for making exact output swaps
 */
function encodeRouteToPath(route, exactOutput) {
  var firstInputToken = route.input.wrapped;
  var _route$pools$reduce = route.pools.reduce(function (_ref, pool, index) {
      var inputToken = _ref.inputToken,
        path = _ref.path,
        types = _ref.types;
      var outputToken = pool.token0.equals(inputToken) ? pool.token1 : pool.token0;
      if (index === 0) {
        return {
          inputToken: outputToken,
          types: ['address', 'address', 'address'],
          path: [inputToken.address, pool.deployer, outputToken.address]
        };
      } else {
        return {
          inputToken: outputToken,
          types: [].concat(types, ['address', 'address']),
          path: [].concat(path, [pool.deployer, outputToken.address])
        };
      }
    }, {
      inputToken: firstInputToken,
      path: [],
      types: []
    }),
    path = _route$pools$reduce.path,
    types = _route$pools$reduce.types;
  return exactOutput ? pack(types.reverse(), path.reverse()) : pack(types, path);
}

var MAX_SAFE_INTEGER = /*#__PURE__*/JSBI.BigInt(Number.MAX_SAFE_INTEGER);
var ZERO$1 = /*#__PURE__*/JSBI.BigInt(0);
var ONE$1 = /*#__PURE__*/JSBI.BigInt(1);
var TWO$1 = /*#__PURE__*/JSBI.BigInt(2);
/**
 * Computes floor(sqrt(value))
 * @param value the value for which to compute the square root, rounded down
 */
function sqrt(value) {
  !JSBI.greaterThanOrEqual(value, ZERO$1) ? process.env.NODE_ENV !== "production" ? invariant(false, 'NEGATIVE') : invariant(false) : void 0;
  // rely on built in sqrt if possible
  if (JSBI.lessThan(value, MAX_SAFE_INTEGER)) {
    return JSBI.BigInt(Math.floor(Math.sqrt(JSBI.toNumber(value))));
  }
  var z;
  var x;
  z = value;
  x = JSBI.add(JSBI.divide(value, TWO$1), ONE$1);
  while (JSBI.lessThan(x, z)) {
    z = x;
    x = JSBI.divide(JSBI.add(JSBI.divide(value, x), x), TWO$1);
  }
  return z;
}

/**
 * Returns the sqrt ratio as a Q64.96 corresponding to a given ratio of amount1 and amount0
 * @param amount1 The numerator amount i.e., the amount of token1
 * @param amount0 The denominator amount i.e., the amount of token0
 * @returns The sqrt ratio
 */
function encodeSqrtRatioX96(amount1, amount0) {
  var numerator = JSBI.leftShift(JSBI.BigInt(amount1), JSBI.BigInt(192));
  var denominator = JSBI.BigInt(amount0);
  var ratioX192 = JSBI.divide(numerator, denominator);
  return sqrt(ratioX192);
}

/**
 * Returns an imprecise maximum amount of liquidity received for a given amount of token 0.
 * This function is available to accommodate LiquidityAmounts#getLiquidityForAmount0 in the v3 periphery,
 * which could be more precise by at least 32 bits by dividing by Q64 instead of Q96 in the intermediate step,
 * and shifting the subtracted ratio left by 32 bits. This imprecise calculation will likely be replaced in a future
 * v3 router contract.
 * @param sqrtRatioAX96 The price at the lower boundary
 * @param sqrtRatioBX96 The price at the upper boundary
 * @param amount0 The token0 amount
 * @returns liquidity for amount0, imprecise
 */
function maxLiquidityForAmount0Imprecise(sqrtRatioAX96, sqrtRatioBX96, amount0) {
  if (JSBI.greaterThan(sqrtRatioAX96, sqrtRatioBX96)) {
    var _ref = [sqrtRatioBX96, sqrtRatioAX96];
    sqrtRatioAX96 = _ref[0];
    sqrtRatioBX96 = _ref[1];
  }
  var intermediate = JSBI.divide(JSBI.multiply(sqrtRatioAX96, sqrtRatioBX96), Q96);
  return JSBI.divide(JSBI.multiply(JSBI.BigInt(amount0), intermediate), JSBI.subtract(sqrtRatioBX96, sqrtRatioAX96));
}
/**
 * Returns a precise maximum amount of liquidity received for a given amount of token 0 by dividing by Q64 instead of Q96 in the intermediate step,
 * and shifting the subtracted ratio left by 32 bits.
 * @param sqrtRatioAX96 The price at the lower boundary
 * @param sqrtRatioBX96 The price at the upper boundary
 * @param amount0 The token0 amount
 * @returns liquidity for amount0, precise
 */
function maxLiquidityForAmount0Precise(sqrtRatioAX96, sqrtRatioBX96, amount0) {
  if (JSBI.greaterThan(sqrtRatioAX96, sqrtRatioBX96)) {
    var _ref2 = [sqrtRatioBX96, sqrtRatioAX96];
    sqrtRatioAX96 = _ref2[0];
    sqrtRatioBX96 = _ref2[1];
  }
  var numerator = JSBI.multiply(JSBI.multiply(JSBI.BigInt(amount0), sqrtRatioAX96), sqrtRatioBX96);
  var denominator = JSBI.multiply(Q96, JSBI.subtract(sqrtRatioBX96, sqrtRatioAX96));
  return JSBI.divide(numerator, denominator);
}
/**
 * Computes the maximum amount of liquidity received for a given amount of token1
 * @param sqrtRatioAX96 The price at the lower tick boundary
 * @param sqrtRatioBX96 The price at the upper tick boundary
 * @param amount1 The token1 amount
 * @returns liquidity for amount1
 */
function maxLiquidityForAmount1(sqrtRatioAX96, sqrtRatioBX96, amount1) {
  if (JSBI.greaterThan(sqrtRatioAX96, sqrtRatioBX96)) {
    var _ref3 = [sqrtRatioBX96, sqrtRatioAX96];
    sqrtRatioAX96 = _ref3[0];
    sqrtRatioBX96 = _ref3[1];
  }
  return JSBI.divide(JSBI.multiply(JSBI.BigInt(amount1), Q96), JSBI.subtract(sqrtRatioBX96, sqrtRatioAX96));
}
/**
 * Computes the maximum amount of liquidity received for a given amount of token0, token1,
 * and the prices at the tick boundaries.
 * @param sqrtRatioCurrentX96 the current price
 * @param sqrtRatioAX96 price at lower boundary
 * @param sqrtRatioBX96 price at upper boundary
 * @param amount0 token0 amount
 * @param amount1 token1 amount
 * @param useFullPrecision if false, liquidity will be maximized according to what the router can calculate,
 * not what core can theoretically support
 */
function maxLiquidityForAmounts(sqrtRatioCurrentX96, sqrtRatioAX96, sqrtRatioBX96, amount0, amount1, useFullPrecision) {
  if (JSBI.greaterThan(sqrtRatioAX96, sqrtRatioBX96)) {
    var _ref4 = [sqrtRatioBX96, sqrtRatioAX96];
    sqrtRatioAX96 = _ref4[0];
    sqrtRatioBX96 = _ref4[1];
  }
  var maxLiquidityForAmount0 = useFullPrecision ? maxLiquidityForAmount0Precise : maxLiquidityForAmount0Imprecise;
  if (JSBI.lessThanOrEqual(sqrtRatioCurrentX96, sqrtRatioAX96)) {
    return maxLiquidityForAmount0(sqrtRatioAX96, sqrtRatioBX96, amount0);
  } else if (JSBI.lessThan(sqrtRatioCurrentX96, sqrtRatioBX96)) {
    var liquidity0 = maxLiquidityForAmount0(sqrtRatioCurrentX96, sqrtRatioBX96, amount0);
    var liquidity1 = maxLiquidityForAmount1(sqrtRatioAX96, sqrtRatioCurrentX96, amount1);
    return JSBI.lessThan(liquidity0, liquidity1) ? liquidity0 : liquidity1;
  } else {
    return maxLiquidityForAmount1(sqrtRatioAX96, sqrtRatioBX96, amount1);
  }
}

/**
 * Returns the closest tick that is nearest a given tick and usable for the given tick spacing
 * @param tick the target tick
 * @param tickSpacing the spacing of the pool
 */
function nearestUsableTick(tick, tickSpacing) {
  !(Number.isInteger(tick) && Number.isInteger(tickSpacing)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INTEGERS') : invariant(false) : void 0;
  !(tickSpacing > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_SPACING') : invariant(false) : void 0;
  !(tick >= TickMath.MIN_TICK && tick <= TickMath.MAX_TICK) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_BOUND') : invariant(false) : void 0;
  var rounded = Math.round(tick / tickSpacing) * tickSpacing;
  if (rounded < TickMath.MIN_TICK) return rounded + tickSpacing;else if (rounded > TickMath.MAX_TICK) return rounded - tickSpacing;else return rounded;
}

var ABS = function ABS(x) {
  return JSBI.lessThan(x, JSBI.BigInt(0)) ? JSBI.multiply(x, JSBI.BigInt(-1)) : x;
};
/**
 * Returns a price object corresponding to the input tick and the base/quote token
 * Inputs must be tokens because the address order is used to interpret the price represented by the tick
 * @param baseToken the base token of the price
 * @param quoteToken the quote token of the price
 * @param tick the tick for which to return the price
 */
function tickToPrice(baseToken, quoteToken, tick) {
  var sqrtRatioX96 = TickMath.getSqrtRatioAtTick(tick);
  var ratioX192 = JSBI.multiply(sqrtRatioX96, sqrtRatioX96);
  return baseToken.sortsBefore(quoteToken) ? new Price(baseToken, quoteToken, Q192, ratioX192) : new Price(baseToken, quoteToken, ratioX192, Q192);
}
/**
 * Returns the first tick for which the given price is greater than or equal to the tick price
 * @param price for which to return the closest tick that represents a price less than or equal to the input price,
 * i.e. the price of the returned tick is less than or equal to the input price
 */
function priceToClosestTick(price) {
  var sorted = price.baseCurrency.sortsBefore(price.quoteCurrency);
  var sqrtInput = sorted ? encodeSqrtRatioX96(price.numerator, price.denominator) : encodeSqrtRatioX96(price.denominator, price.numerator);
  // initial tick
  var tick = TickMath.getTickAtSqrtRatio(sqrtInput);
  // check tick-1, tick, tick+1
  var candidates = [tick - 1, tick, tick + 1].filter(function (t) {
    return t >= TickMath.MIN_TICK && t <= TickMath.MAX_TICK;
  });
  var bestTick = tick;
  var bestDiff = ABS(JSBI.subtract(sqrtInput, TickMath.getSqrtRatioAtTick(tick)));
  for (var _iterator = _createForOfIteratorHelperLoose(candidates), _step; !(_step = _iterator()).done;) {
    var t = _step.value;
    var diff = ABS(JSBI.subtract(sqrtInput, TickMath.getSqrtRatioAtTick(t)));
    if (JSBI.lessThan(diff, bestDiff)) {
      bestDiff = diff;
      bestTick = t;
    }
  }
  return bestTick;
}

function getTickToPrice(baseToken, quoteToken, tick) {
  if (!baseToken || !quoteToken || typeof tick !== 'number') {
    return undefined;
  }
  return tickToPrice(baseToken, quoteToken, tick);
}

var Tick = function Tick(_ref) {
  var index = _ref.index,
    liquidityGross = _ref.liquidityGross,
    liquidityNet = _ref.liquidityNet;
  !(index >= TickMath.MIN_TICK && index <= TickMath.MAX_TICK) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK') : invariant(false) : void 0;
  this.index = index;
  this.liquidityGross = JSBI.BigInt(liquidityGross);
  this.liquidityNet = JSBI.BigInt(liquidityNet);
};

/**
 * A data provider for ticks that is backed by an in-memory array of ticks.
 */
var TickListDataProvider = /*#__PURE__*/function () {
  function TickListDataProvider(ticks, tickSpacing) {
    var ticksMapped = ticks.map(function (t) {
      return t instanceof Tick ? t : new Tick(t);
    });
    TickList.validateList(ticksMapped, tickSpacing);
    this.ticks = ticksMapped;
  }
  var _proto = TickListDataProvider.prototype;
  _proto.getTick = /*#__PURE__*/function () {
    var _getTick = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee(tick) {
      return _regeneratorRuntime().wrap(function _callee$(_context) {
        while (1) switch (_context.prev = _context.next) {
          case 0:
            return _context.abrupt("return", TickList.getTick(this.ticks, tick));
          case 1:
          case "end":
            return _context.stop();
        }
      }, _callee, this);
    }));
    function getTick(_x) {
      return _getTick.apply(this, arguments);
    }
    return getTick;
  }();
  _proto.nextInitializedTickWithinOneWord = /*#__PURE__*/function () {
    var _nextInitializedTickWithinOneWord = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee2(tick, lte, tickSpacing) {
      return _regeneratorRuntime().wrap(function _callee2$(_context2) {
        while (1) switch (_context2.prev = _context2.next) {
          case 0:
            return _context2.abrupt("return", TickList.nextInitializedTickWithinOneWord(this.ticks, tick, lte, tickSpacing));
          case 1:
          case "end":
            return _context2.stop();
        }
      }, _callee2, this);
    }));
    function nextInitializedTickWithinOneWord(_x2, _x3, _x4) {
      return _nextInitializedTickWithinOneWord.apply(this, arguments);
    }
    return nextInitializedTickWithinOneWord;
  }();
  return TickListDataProvider;
}();

function sortsBefore(currencyA, currencyB) {
  if (currencyA.isNative) return true;
  if (currencyB.isNative) return false;
  return currencyA.wrapped.sortsBefore(currencyB.wrapped);
}

/**
 * By default, pools will not allow operations that require ticks.
 */
var NO_TICK_DATA_PROVIDER_DEFAULT = /*#__PURE__*/new NoTickDataProvider();
/**
 * Represents a V3 pool
 */
var Pool = /*#__PURE__*/function () {
  /**
   * Construct a pool
   * @param tokenA One of the tokens in the pool
   * @param tokenB The other token in the pool
   * @param fee The fee in hundredths of a bips of the input amount of every swap that is collected by the pool
   * @param sqrtRatioX96 The sqrt of the current ratio of amounts of token1 to token0
   * @param liquidity The current value of in range liquidity
   * @param tickCurrent The current tick of the pool
   * @param ticks The current state of the pool ticks or a data provider that can return tick data
   * @param _tickSpacing The spacing between ticks
   */
  function Pool(tokenA, tokenB, fee, sqrtRatioX96, deployer, liquidity, tickCurrent, _tickSpacing, ticks) {
    if (ticks === void 0) {
      ticks = NO_TICK_DATA_PROVIDER_DEFAULT;
    }
    !(Number.isInteger(fee) && fee < 1000000) ? process.env.NODE_ENV !== "production" ? invariant(false, 'FEE') : invariant(false) : void 0;
    var tickCurrentSqrtRatioX96 = TickMath.getSqrtRatioAtTick(tickCurrent);
    var nextTickSqrtRatioX96 = TickMath.getSqrtRatioAtTick(tickCurrent + 1);
    !(JSBI.greaterThanOrEqual(JSBI.BigInt(sqrtRatioX96), tickCurrentSqrtRatioX96) && JSBI.lessThanOrEqual(JSBI.BigInt(sqrtRatioX96), nextTickSqrtRatioX96)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'PRICE_BOUNDS') : invariant(false) : void 0;
    // always create a copy of the list since we want the pool's tick list to be immutable
    var _ref = sortsBefore(tokenA, tokenB) ? [tokenA, tokenB] : [tokenB, tokenA];
    this.token0 = _ref[0];
    this.token1 = _ref[1];
    this.fee = fee;
    this.sqrtRatioX96 = JSBI.BigInt(sqrtRatioX96);
    this.deployer = deployer;
    this.liquidity = JSBI.BigInt(liquidity);
    this.tickCurrent = tickCurrent;
    this.tickDataProvider = Array.isArray(ticks) ? new TickListDataProvider(ticks, _tickSpacing) : ticks;
    this._tickSpacing = _tickSpacing;
  }
  /**
   * Returns the current mid price of the pool in terms of token0, i.e. the ratio of token1 over token0
   */
  Pool.getAddress = function getAddress(tokenA, tokenB, initCodeHashManualOverride) {
    return computePoolAddress({
      poolDeployer: POOL_DEPLOYER_ADDRESSES[tokenA.chainId],
      tokenA: tokenA,
      tokenB: tokenB,
      initCodeHashManualOverride: initCodeHashManualOverride
    });
  }
  /**
   * Returns true if the token is either token0 or token1
   * @param token The token to check
   * @returns True if token is either token0 or token
   */;
  var _proto = Pool.prototype;
  _proto.involvesToken = function involvesToken(token) {
    return token.equals(this.token0) || token.equals(this.token1);
  }
  /**
   * Return the price of the given token in terms of the other token in the pool.
   * @param token The token to return price of
   * @returns The price of the given token, in terms of the other.
   */;
  _proto.priceOf = function priceOf(token) {
    !this.involvesToken(token) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN') : invariant(false) : void 0;
    return token.equals(this.token0) ? this.token0Price : this.token1Price;
  }
  /**
   * Given an input amount of a token, return the computed output amount, and a pool with state updated after the trade
   * @param inputAmount The input amount for which to quote the output amount
   * @param sqrtPriceLimitX96 The Q64.96 sqrt price limit
   * @returns The output amount and the pool with updated state
   */;
  _proto.getOutputAmount =
  /*#__PURE__*/
  function () {
    var _getOutputAmount = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee(inputAmount, sqrtPriceLimitX96) {
      var zeroForOne, _yield$this$swap, outputAmount, sqrtRatioX96, liquidity, tickCurrent, outputToken;
      return _regeneratorRuntime().wrap(function _callee$(_context) {
        while (1) switch (_context.prev = _context.next) {
          case 0:
            !this.involvesToken(inputAmount.currency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN') : invariant(false) : void 0;
            zeroForOne = inputAmount.currency.equals(this.token0);
            _context.next = 4;
            return this.swap(zeroForOne, inputAmount.quotient, sqrtPriceLimitX96);
          case 4:
            _yield$this$swap = _context.sent;
            outputAmount = _yield$this$swap.amountCalculated;
            sqrtRatioX96 = _yield$this$swap.sqrtRatioX96;
            liquidity = _yield$this$swap.liquidity;
            tickCurrent = _yield$this$swap.tickCurrent;
            outputToken = zeroForOne ? this.token1 : this.token0;
            return _context.abrupt("return", [CurrencyAmount.fromRawAmount(outputToken, JSBI.multiply(outputAmount, NEGATIVE_ONE)), new Pool(this.token0, this.token1, this.fee, sqrtRatioX96, this.deployer, liquidity, tickCurrent, this.tickSpacing, this.tickDataProvider)]);
          case 11:
          case "end":
            return _context.stop();
        }
      }, _callee, this);
    }));
    function getOutputAmount(_x, _x2) {
      return _getOutputAmount.apply(this, arguments);
    }
    return getOutputAmount;
  }()
  /**
   * Given a desired output amount of a token, return the computed input amount and a pool with state updated after the trade
   * @param outputAmount the output amount for which to quote the input amount
   * @param sqrtPriceLimitX96 The Q64.96 sqrt price limit. If zero for one, the price cannot be less than this value after the swap. If one for zero, the price cannot be greater than this value after the swap
   * @returns The input amount and the pool with updated state
   */
  ;
  _proto.getInputAmount =
  /*#__PURE__*/
  function () {
    var _getInputAmount = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee2(outputAmount, sqrtPriceLimitX96) {
      var zeroForOne, _yield$this$swap2, inputAmount, sqrtRatioX96, liquidity, tickCurrent, inputToken;
      return _regeneratorRuntime().wrap(function _callee2$(_context2) {
        while (1) switch (_context2.prev = _context2.next) {
          case 0:
            !(outputAmount.currency.isToken && this.involvesToken(outputAmount.currency)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN') : invariant(false) : void 0;
            zeroForOne = outputAmount.currency.equals(this.token1);
            _context2.next = 4;
            return this.swap(zeroForOne, JSBI.multiply(outputAmount.quotient, NEGATIVE_ONE), sqrtPriceLimitX96);
          case 4:
            _yield$this$swap2 = _context2.sent;
            inputAmount = _yield$this$swap2.amountCalculated;
            sqrtRatioX96 = _yield$this$swap2.sqrtRatioX96;
            liquidity = _yield$this$swap2.liquidity;
            tickCurrent = _yield$this$swap2.tickCurrent;
            inputToken = zeroForOne ? this.token0 : this.token1;
            return _context2.abrupt("return", [CurrencyAmount.fromRawAmount(inputToken, inputAmount), new Pool(this.token0, this.token1, this.fee, sqrtRatioX96, this.deployer, liquidity, tickCurrent, this.tickSpacing, this.tickDataProvider)]);
          case 11:
          case "end":
            return _context2.stop();
        }
      }, _callee2, this);
    }));
    function getInputAmount(_x3, _x4) {
      return _getInputAmount.apply(this, arguments);
    }
    return getInputAmount;
  }()
  /**
   * Executes a swap
   * @param zeroForOne Whether the amount in is token0 or token1
   * @param amountSpecified The amount of the swap, which implicitly configures the swap as exact input (positive), or exact output (negative)
   * @param sqrtPriceLimitX96 The Q64.96 sqrt price limit. If zero for one, the price cannot be less than this value after the swap. If one for zero, the price cannot be greater than this value after the swap
   * @returns amountCalculated
   * @returns sqrtRatioX96
   * @returns liquidity
   * @returns tickCurrent
   */
  ;
  _proto.swap =
  /*#__PURE__*/
  function () {
    var _swap = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee3(zeroForOne, amountSpecified, sqrtPriceLimitX96) {
      var exactInput, state, step, _yield$this$tickDataP, _SwapMath$computeSwap, liquidityNet;
      return _regeneratorRuntime().wrap(function _callee3$(_context3) {
        while (1) switch (_context3.prev = _context3.next) {
          case 0:
            if (!sqrtPriceLimitX96) sqrtPriceLimitX96 = zeroForOne ? JSBI.add(TickMath.MIN_SQRT_RATIO, ONE) : JSBI.subtract(TickMath.MAX_SQRT_RATIO, ONE);
            if (zeroForOne) {
              !JSBI.greaterThan(sqrtPriceLimitX96, TickMath.MIN_SQRT_RATIO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'RATIO_MIN') : invariant(false) : void 0;
              !JSBI.lessThan(sqrtPriceLimitX96, this.sqrtRatioX96) ? process.env.NODE_ENV !== "production" ? invariant(false, 'RATIO_CURRENT') : invariant(false) : void 0;
            } else {
              !JSBI.lessThan(sqrtPriceLimitX96, TickMath.MAX_SQRT_RATIO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'RATIO_MAX') : invariant(false) : void 0;
              !JSBI.greaterThan(sqrtPriceLimitX96, this.sqrtRatioX96) ? process.env.NODE_ENV !== "production" ? invariant(false, 'RATIO_CURRENT') : invariant(false) : void 0;
            }
            exactInput = JSBI.greaterThanOrEqual(amountSpecified, ZERO); // keep track of swap state
            state = {
              amountSpecifiedRemaining: amountSpecified,
              amountCalculated: ZERO,
              sqrtPriceX96: this.sqrtRatioX96,
              tick: this.tickCurrent,
              liquidity: this.liquidity
            }; // start swap while loop
          case 4:
            if (!(JSBI.notEqual(state.amountSpecifiedRemaining, ZERO) && state.sqrtPriceX96 != sqrtPriceLimitX96)) {
              _context3.next = 35;
              break;
            }
            step = {};
            step.sqrtPriceStartX96 = state.sqrtPriceX96;
            // because each iteration of the while loop rounds, we can't optimize this code (relative to the smart contract)
            // by simply traversing to the next available tick, we instead need to exactly replicate
            // tickBitmap.nextInitializedTickWithinOneWord
            _context3.next = 9;
            return this.tickDataProvider.nextInitializedTickWithinOneWord(state.tick, zeroForOne, this.tickSpacing);
          case 9:
            _yield$this$tickDataP = _context3.sent;
            step.tickNext = _yield$this$tickDataP[0];
            step.initialized = _yield$this$tickDataP[1];
            if (step.tickNext < TickMath.MIN_TICK) {
              step.tickNext = TickMath.MIN_TICK;
            } else if (step.tickNext > TickMath.MAX_TICK) {
              step.tickNext = TickMath.MAX_TICK;
            }
            step.sqrtPriceNextX96 = TickMath.getSqrtRatioAtTick(step.tickNext);
            _SwapMath$computeSwap = SwapMath.computeSwapStep(state.sqrtPriceX96, (zeroForOne ? JSBI.lessThan(step.sqrtPriceNextX96, sqrtPriceLimitX96) : JSBI.greaterThan(step.sqrtPriceNextX96, sqrtPriceLimitX96)) ? sqrtPriceLimitX96 : step.sqrtPriceNextX96, state.liquidity, state.amountSpecifiedRemaining, this.fee);
            state.sqrtPriceX96 = _SwapMath$computeSwap[0];
            step.amountIn = _SwapMath$computeSwap[1];
            step.amountOut = _SwapMath$computeSwap[2];
            step.feeAmount = _SwapMath$computeSwap[3];
            if (exactInput) {
              state.amountSpecifiedRemaining = JSBI.subtract(state.amountSpecifiedRemaining, JSBI.add(step.amountIn, step.feeAmount));
              state.amountCalculated = JSBI.subtract(state.amountCalculated, step.amountOut);
            } else {
              state.amountSpecifiedRemaining = JSBI.add(state.amountSpecifiedRemaining, step.amountOut);
              state.amountCalculated = JSBI.add(state.amountCalculated, JSBI.add(step.amountIn, step.feeAmount));
            }
            // TODO
            if (!JSBI.equal(state.sqrtPriceX96, step.sqrtPriceNextX96)) {
              _context3.next = 32;
              break;
            }
            if (!step.initialized) {
              _context3.next = 29;
              break;
            }
            _context3.t0 = JSBI;
            _context3.next = 25;
            return this.tickDataProvider.getTick(step.tickNext);
          case 25:
            _context3.t1 = _context3.sent.liquidityNet;
            liquidityNet = _context3.t0.BigInt.call(_context3.t0, _context3.t1);
            // if we're moving leftward, we interpret liquidityNet as the opposite sign
            // safe because liquidityNet cannot be type(int128).min
            if (zeroForOne) liquidityNet = JSBI.multiply(liquidityNet, NEGATIVE_ONE);
            state.liquidity = LiquidityMath.addDelta(state.liquidity, liquidityNet);
          case 29:
            state.tick = zeroForOne ? step.tickNext - 1 : step.tickNext;
            _context3.next = 33;
            break;
          case 32:
            if (state.sqrtPriceX96 != step.sqrtPriceStartX96) {
              // recompute unless we're on a lower tick boundary (i.e. already transitioned ticks), and haven't moved
              state.tick = TickMath.getTickAtSqrtRatio(state.sqrtPriceX96);
            }
          case 33:
            _context3.next = 4;
            break;
          case 35:
            return _context3.abrupt("return", {
              amountCalculated: state.amountCalculated,
              sqrtRatioX96: state.sqrtPriceX96,
              liquidity: state.liquidity,
              tickCurrent: state.tick
            });
          case 36:
          case "end":
            return _context3.stop();
        }
      }, _callee3, this);
    }));
    function swap(_x5, _x6, _x7) {
      return _swap.apply(this, arguments);
    }
    return swap;
  }();
  _createClass(Pool, [{
    key: "token0Price",
    get: function get() {
      var _this$_token0Price;
      return (_this$_token0Price = this._token0Price) != null ? _this$_token0Price : this._token0Price = new Price(this.token0, this.token1, Q192, JSBI.multiply(this.sqrtRatioX96, this.sqrtRatioX96));
    }
    /**
     * Returns the current mid price of the pool in terms of token1, i.e. the ratio of token0 over token1
     */
  }, {
    key: "token1Price",
    get: function get() {
      var _this$_token1Price;
      return (_this$_token1Price = this._token1Price) != null ? _this$_token1Price : this._token1Price = new Price(this.token1, this.token0, JSBI.multiply(this.sqrtRatioX96, this.sqrtRatioX96), Q192);
    }
    /**
     * Returns the chain ID of the tokens in the pool.
     */
  }, {
    key: "chainId",
    get: function get() {
      return this.token0.chainId;
    }
  }, {
    key: "tickSpacing",
    get: function get() {
      return this._tickSpacing;
    }
  }]);
  return Pool;
}();

/**
 * Represents a position on a Algebra Pool
 */
var Position = /*#__PURE__*/function () {
  /**
   * Constructs a position for a given pool with the given liquidity
   * @param pool For which pool the liquidity is assigned
   * @param liquidity The amount of liquidity that is in the position
   * @param tickLower The lower tick of the position
   * @param tickUpper The upper tick of the position
   */
  function Position(_ref) {
    var pool = _ref.pool,
      liquidity = _ref.liquidity,
      tickLower = _ref.tickLower,
      tickUpper = _ref.tickUpper;
    // cached resuts for the getters
    this._token0Amount = null;
    this._token1Amount = null;
    this._mintAmounts = null;
    !(tickLower < tickUpper) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_ORDER') : invariant(false) : void 0;
    !(tickLower >= TickMath.MIN_TICK && tickLower % pool.tickSpacing === 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_LOWER') : invariant(false) : void 0;
    !(tickUpper <= TickMath.MAX_TICK && tickUpper % pool.tickSpacing === 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TICK_UPPER') : invariant(false) : void 0;
    this.pool = pool;
    this.tickLower = tickLower;
    this.tickUpper = tickUpper;
    this.liquidity = JSBI.BigInt(liquidity);
  }
  /**
   * Returns the minimum amounts that must be sent in order to mint the amount of liquidity held by the position at
   * the current price for the pool
   */
  /**
   * Computes the maximum amount of liquidity received for a given amount of token0, token1,
   * and the prices at the tick boundaries.
   * @param pool The pool for which the position should be created
   * @param tickLower The lower tick of the position
   * @param tickUpper The upper tick of the position
   * @param amount0 token0 amount
   * @param amount1 token1 amount
   * @param useFullPrecision If false, liquidity will be maximized according to what the router can calculate,
   * not what core can theoretically support
   * @returns The amount of liquidity for the position
   */
  Position.fromAmounts = function fromAmounts(_ref2) {
    var pool = _ref2.pool,
      tickLower = _ref2.tickLower,
      tickUpper = _ref2.tickUpper,
      amount0 = _ref2.amount0,
      amount1 = _ref2.amount1,
      useFullPrecision = _ref2.useFullPrecision;
    var sqrtRatioAX96 = TickMath.getSqrtRatioAtTick(tickLower);
    var sqrtRatioBX96 = TickMath.getSqrtRatioAtTick(tickUpper);
    return new Position({
      pool: pool,
      tickLower: tickLower,
      tickUpper: tickUpper,
      liquidity: maxLiquidityForAmounts(pool.sqrtRatioX96, sqrtRatioAX96, sqrtRatioBX96, amount0, amount1, useFullPrecision)
    });
  }
  /**
   * Computes a position with the maximum amount of liquidity received for a given amount of token0, assuming an unlimited amount of token1
   * @param pool The pool for which the position is created
   * @param tickLower The lower tick
   * @param tickUpper The upper tick
   * @param amount0 The desired amount of token0
   * @param useFullPrecision If true, liquidity will be maximized according to what the router can calculate,
   * not what core can theoretically support
   * @returns The position
   */;
  Position.fromAmount0 = function fromAmount0(_ref3) {
    var pool = _ref3.pool,
      tickLower = _ref3.tickLower,
      tickUpper = _ref3.tickUpper,
      amount0 = _ref3.amount0,
      useFullPrecision = _ref3.useFullPrecision;
    return Position.fromAmounts({
      pool: pool,
      tickLower: tickLower,
      tickUpper: tickUpper,
      amount0: amount0,
      amount1: MaxUint256,
      useFullPrecision: useFullPrecision
    });
  }
  /**
   * Computes a position with the maximum amount of liquidity received for a given amount of token1, assuming an unlimited amount of token0
   * @param pool The pool for which the position is created
   * @param tickLower The lower tick
   * @param tickUpper The upper tick
   * @param amount1 The desired amount of token1
   * @returns The position
   */;
  Position.fromAmount1 = function fromAmount1(_ref4) {
    var pool = _ref4.pool,
      tickLower = _ref4.tickLower,
      tickUpper = _ref4.tickUpper,
      amount1 = _ref4.amount1;
    // this function always uses full precision,
    return Position.fromAmounts({
      pool: pool,
      tickLower: tickLower,
      tickUpper: tickUpper,
      amount0: MaxUint256,
      amount1: amount1,
      useFullPrecision: true
    });
  }
  /**
   * Returns the minimum amounts that must be sent in order to safely mint the amount of liquidity held by the position
   * with the given slippage tolerance
   * @param slippageTolerance Tolerance of unfavorable slippage from the current price
   * @returns The amounts, with slippage
   */;
  var _proto = Position.prototype;
  _proto.mintAmountsWithSlippage = function mintAmountsWithSlippage(slippageTolerance) {
    // get lower/upper prices
    var _this$ratiosAfterSlip = this.ratiosAfterSlippage(slippageTolerance),
      sqrtRatioX96Upper = _this$ratiosAfterSlip.sqrtRatioX96Upper,
      sqrtRatioX96Lower = _this$ratiosAfterSlip.sqrtRatioX96Lower;
    // construct counterfactual pools
    var poolLower = new Pool(this.pool.token0, this.pool.token1, this.pool.fee, sqrtRatioX96Lower, this.pool.deployer, 0 /* liquidity doesn't matter */, TickMath.getTickAtSqrtRatio(sqrtRatioX96Lower), this.pool.tickSpacing);
    var poolUpper = new Pool(this.pool.token0, this.pool.token1, this.pool.fee, sqrtRatioX96Upper, this.pool.deployer, 0 /* liquidity doesn't matter */, TickMath.getTickAtSqrtRatio(sqrtRatioX96Upper), this.pool.tickSpacing);
    // because the router is imprecise, we need to calculate the position that will be created (assuming no slippage)
    var positionThatWillBeCreated = Position.fromAmounts(_extends({
      pool: this.pool,
      tickLower: this.tickLower,
      tickUpper: this.tickUpper
    }, this.mintAmounts, {
      useFullPrecision: false
    }));
    // we want the smaller amounts...
    // ...which occurs at the upper price for amount0...
    var amount0 = new Position({
      pool: poolUpper,
      liquidity: positionThatWillBeCreated.liquidity,
      tickLower: this.tickLower,
      tickUpper: this.tickUpper
    }).mintAmounts.amount0;
    // ...and the lower for amount1
    var amount1 = new Position({
      pool: poolLower,
      liquidity: positionThatWillBeCreated.liquidity,
      tickLower: this.tickLower,
      tickUpper: this.tickUpper
    }).mintAmounts.amount1;
    return {
      amount0: amount0,
      amount1: amount1
    };
  }
  /**
   * Returns the minimum amounts that should be requested in order to safely burn the amount of liquidity held by the
   * position with the given slippage tolerance
   * @param slippageTolerance tolerance of unfavorable slippage from the current price
   * @returns The amounts, with slippage
   */;
  _proto.burnAmountsWithSlippage = function burnAmountsWithSlippage(slippageTolerance) {
    // get lower/upper prices
    var _this$ratiosAfterSlip2 = this.ratiosAfterSlippage(slippageTolerance),
      sqrtRatioX96Upper = _this$ratiosAfterSlip2.sqrtRatioX96Upper,
      sqrtRatioX96Lower = _this$ratiosAfterSlip2.sqrtRatioX96Lower;
    // construct counterfactual pools
    var poolLower = new Pool(this.pool.token0, this.pool.token1, this.pool.fee, sqrtRatioX96Lower, this.pool.deployer, 0 /* liquidity doesn't matter */, TickMath.getTickAtSqrtRatio(sqrtRatioX96Lower), this.pool.tickSpacing);
    var poolUpper = new Pool(this.pool.token0, this.pool.token1, this.pool.fee, sqrtRatioX96Upper, this.pool.deployer, 0 /* liquidity doesn't matter */, TickMath.getTickAtSqrtRatio(sqrtRatioX96Upper), this.pool.tickSpacing);
    // we want the smaller amounts...
    // ...which occurs at the upper price for amount0...
    var amount0 = new Position({
      pool: poolUpper,
      liquidity: this.liquidity,
      tickLower: this.tickLower,
      tickUpper: this.tickUpper
    }).amount0;
    // ...and the lower for amount1
    var amount1 = new Position({
      pool: poolLower,
      liquidity: this.liquidity,
      tickLower: this.tickLower,
      tickUpper: this.tickUpper
    }).amount1;
    return {
      amount0: amount0.quotient,
      amount1: amount1.quotient
    };
  }
  /**
   * Returns the lower and upper sqrt ratios if the price 'slips' up to slippage tolerance percentage
   * @param slippageTolerance The amount by which the price can 'slip' before the transaction will revert
   * @returns The sqrt ratios after slippage
   */;
  _proto.ratiosAfterSlippage = function ratiosAfterSlippage(slippageTolerance) {
    var priceLower = this.pool.token0Price.asFraction.multiply(new Percent(1).subtract(slippageTolerance));
    var priceUpper = this.pool.token0Price.asFraction.multiply(slippageTolerance.add(1));
    var sqrtRatioX96Lower = encodeSqrtRatioX96(priceLower.numerator, priceLower.denominator);
    if (JSBI.lessThanOrEqual(sqrtRatioX96Lower, TickMath.MIN_SQRT_RATIO)) {
      sqrtRatioX96Lower = JSBI.add(TickMath.MIN_SQRT_RATIO, JSBI.BigInt(1));
    }
    var sqrtRatioX96Upper = encodeSqrtRatioX96(priceUpper.numerator, priceUpper.denominator);
    if (JSBI.greaterThanOrEqual(sqrtRatioX96Upper, TickMath.MAX_SQRT_RATIO)) {
      sqrtRatioX96Upper = JSBI.subtract(TickMath.MAX_SQRT_RATIO, JSBI.BigInt(1));
    }
    return {
      sqrtRatioX96Lower: sqrtRatioX96Lower,
      sqrtRatioX96Upper: sqrtRatioX96Upper
    };
  };
  _createClass(Position, [{
    key: "mintAmounts",
    get: function get() {
      if (this._mintAmounts === null) {
        if (this.pool.tickCurrent < this.tickLower) {
          return {
            amount0: SqrtPriceMath.getAmount0Delta(TickMath.getSqrtRatioAtTick(this.tickLower), TickMath.getSqrtRatioAtTick(this.tickUpper), this.liquidity, true),
            amount1: ZERO
          };
        } else if (this.pool.tickCurrent < this.tickUpper) {
          return {
            amount0: SqrtPriceMath.getAmount0Delta(this.pool.sqrtRatioX96, TickMath.getSqrtRatioAtTick(this.tickUpper), this.liquidity, true),
            amount1: SqrtPriceMath.getAmount1Delta(TickMath.getSqrtRatioAtTick(this.tickLower), this.pool.sqrtRatioX96, this.liquidity, true)
          };
        } else {
          return {
            amount0: ZERO,
            amount1: SqrtPriceMath.getAmount1Delta(TickMath.getSqrtRatioAtTick(this.tickLower), TickMath.getSqrtRatioAtTick(this.tickUpper), this.liquidity, true)
          };
        }
      }
      return this._mintAmounts;
    }
    /**
     * Returns the price of token0 at the lower tick
     */
  }, {
    key: "token0PriceLower",
    get: function get() {
      return tickToPrice(this.pool.token0, this.pool.token1, this.tickLower);
    }
    /**
     * Returns the price of token0 at the upper tick
     */
  }, {
    key: "token0PriceUpper",
    get: function get() {
      return tickToPrice(this.pool.token0, this.pool.token1, this.tickUpper);
    }
    /**
     * Returns the amount of token0 that this position's liquidity could be burned for at the current pool price
     */
  }, {
    key: "amount0",
    get: function get() {
      if (this._token0Amount === null) {
        if (this.pool.tickCurrent < this.tickLower) {
          this._token0Amount = CurrencyAmount.fromRawAmount(this.pool.token0, SqrtPriceMath.getAmount0Delta(TickMath.getSqrtRatioAtTick(this.tickLower), TickMath.getSqrtRatioAtTick(this.tickUpper), this.liquidity, false));
        } else if (this.pool.tickCurrent < this.tickUpper) {
          this._token0Amount = CurrencyAmount.fromRawAmount(this.pool.token0, SqrtPriceMath.getAmount0Delta(this.pool.sqrtRatioX96, TickMath.getSqrtRatioAtTick(this.tickUpper), this.liquidity, false));
        } else {
          this._token0Amount = CurrencyAmount.fromRawAmount(this.pool.token0, ZERO);
        }
      }
      return this._token0Amount;
    }
    /**
     * Returns the amount of token1 that this position's liquidity could be burned for at the current pool price
     */
  }, {
    key: "amount1",
    get: function get() {
      if (this._token1Amount === null) {
        if (this.pool.tickCurrent < this.tickLower) {
          this._token1Amount = CurrencyAmount.fromRawAmount(this.pool.token1, ZERO);
        } else if (this.pool.tickCurrent < this.tickUpper) {
          this._token1Amount = CurrencyAmount.fromRawAmount(this.pool.token1, SqrtPriceMath.getAmount1Delta(TickMath.getSqrtRatioAtTick(this.tickLower), this.pool.sqrtRatioX96, this.liquidity, false));
        } else {
          this._token1Amount = CurrencyAmount.fromRawAmount(this.pool.token1, SqrtPriceMath.getAmount1Delta(TickMath.getSqrtRatioAtTick(this.tickLower), TickMath.getSqrtRatioAtTick(this.tickUpper), this.liquidity, false));
        }
      }
      return this._token1Amount;
    }
  }]);
  return Position;
}();

/**
 * Represents a list of pools through which a swap can occur
 * @template TInput The input token
 * @template TOutput The output token
 */
var Route = /*#__PURE__*/function () {
  /**
   * Creates an instance of route.
   * @param pools An array of `Pool` objects, ordered by the route the swap will take
   * @param input The input token
   * @param output The output token
   */
  function Route(pools, input, output) {
    this.isBoosted = false;
    this._midPrice = null;
    !(pools.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'POOLS') : invariant(false) : void 0;
    var chainId = pools[0].chainId;
    var allOnSameChain = pools.every(function (pool) {
      return pool.chainId === chainId;
    });
    !allOnSameChain ? process.env.NODE_ENV !== "production" ? invariant(false, 'CHAIN_IDS') : invariant(false) : void 0;
    var wrappedInput = input.wrapped;
    !pools[0].involvesToken(wrappedInput) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INPUT') : invariant(false) : void 0;
    !pools[pools.length - 1].involvesToken(output.wrapped) ? process.env.NODE_ENV !== "production" ? invariant(false, 'OUTPUT') : invariant(false) : void 0;
    /**
     * Normalizes token0-token1 order and selects the next token/fee step to add to the path
     * */
    var tokenPath = [wrappedInput];
    for (var _iterator = _createForOfIteratorHelperLoose(pools.entries()), _step; !(_step = _iterator()).done;) {
      var _step$value = _step.value,
        i = _step$value[0],
        pool = _step$value[1];
      var currentInputToken = tokenPath[i];
      !(currentInputToken.equals(pool.token0) || currentInputToken.equals(pool.token1)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'PATH') : invariant(false) : void 0;
      var nextToken = currentInputToken.equals(pool.token0) ? pool.token1 : pool.token0;
      tokenPath.push(nextToken);
    }
    this.pools = pools;
    this.tokenPath = tokenPath;
    this.input = input;
    this.output = output != null ? output : tokenPath[tokenPath.length - 1];
  }
  /**
   * Returns the mid price of the route
   */
  _createClass(Route, [{
    key: "midPrice",
    get: function get() {
      if (this._midPrice !== null) return this._midPrice;
      var price = this.pools.slice(1).reduce(function (_ref, pool) {
        var nextInput = _ref.nextInput,
          price = _ref.price;
        return nextInput.equals(pool.token0) ? {
          nextInput: pool.token1,
          price: price.multiply(pool.token0Price)
        } : {
          nextInput: pool.token0,
          price: price.multiply(pool.token1Price)
        };
      }, this.pools[0].token0.equals(this.input.wrapped) ? {
        nextInput: this.pools[0].token1,
        price: this.pools[0].token0Price
      } : {
        nextInput: this.pools[0].token0,
        price: this.pools[0].token1Price
      }).price;
      return this._midPrice = new Price(this.input, this.output, price.denominator, price.numerator);
    }
  }, {
    key: "chainId",
    get: function get() {
      return this.pools[0].chainId;
    }
  }]);
  return Route;
}();

// given an array of items sorted by `comparator`, insert an item into its sort index and constrain the size to
// `maxSize` by removing the last item
function sortedInsert(items, add, maxSize, comparator) {
  !(maxSize > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'MAX_SIZE_ZERO') : invariant(false) : void 0;
  // this is an invariant because the interface cannot return multiple removed items if items.length exceeds maxSize
  !(items.length <= maxSize) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ITEMS_SIZE') : invariant(false) : void 0;
  // short circuit first item add
  if (items.length === 0) {
    items.push(add);
    return null;
  } else {
    var isFull = items.length === maxSize;
    // short circuit if full and the additional item does not come before the last item
    if (isFull && comparator(items[items.length - 1], add) <= 0) {
      return add;
    }
    var lo = 0,
      hi = items.length;
    while (lo < hi) {
      var mid = lo + hi >>> 1;
      if (comparator(items[mid], add) <= 0) {
        lo = mid + 1;
      } else {
        hi = mid;
      }
    }
    items.splice(lo, 0, add);
    return isFull ? items.pop() : null;
  }
}

var TradeType;
(function (TradeType) {
  TradeType[TradeType["EXACT_INPUT"] = 0] = "EXACT_INPUT";
  TradeType[TradeType["EXACT_OUTPUT"] = 1] = "EXACT_OUTPUT";
})(TradeType || (TradeType = {}));

/**
 * Trades comparator, an extension of the input output comparator that also considers other dimensions of the trade in ranking them
 * @template TInput The input token, either Ether or an ERC-20
 * @template TOutput The output token, either Ether or an ERC-20
 * @template TTradeType The trade type, either exact input or exact output
 * @param a The first trade to compare
 * @param b The second trade to compare
 * @returns A sorted ordering for two neighboring elements in a trade array
 */
function tradeComparator(a, b) {
  // must have same input and output token for comparison
  !a.inputAmount.currency.equals(b.inputAmount.currency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INPUT_CURRENCY') : invariant(false) : void 0;
  !a.outputAmount.currency.equals(b.outputAmount.currency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'OUTPUT_CURRENCY') : invariant(false) : void 0;
  if (a.outputAmount.equalTo(b.outputAmount)) {
    if (a.inputAmount.equalTo(b.inputAmount)) {
      // consider the number of hops since each hop costs gas
      var aHops = a.swaps.reduce(function (total, cur) {
        return total + cur.route.tokenPath.length;
      }, 0);
      var bHops = b.swaps.reduce(function (total, cur) {
        return total + cur.route.tokenPath.length;
      }, 0);
      return aHops - bHops;
    }
    // trade A requires less input than trade B, so A should come first
    if (a.inputAmount.lessThan(b.inputAmount)) {
      return -1;
    } else {
      return 1;
    }
  } else {
    // tradeA has less output than trade B, so should come second
    if (a.outputAmount.lessThan(b.outputAmount)) {
      return 1;
    } else {
      return -1;
    }
  }
}
/**
 * Represents a trade executed against a set of routes where some percentage of the input is
 * split across each route.
 *
 * Each route has its own set of pools. Pools can not be re-used across routes.
 *
 * Does not account for slippage, i.e., changes in price environment that can occur between
 * the time the trade is submitted and when it is executed.
 * @template TInput The input token, either Ether or an ERC-20
 * @template TOutput The output token, either Ether or an ERC-20
 * @template TTradeType The trade type, either exact input or exact output
 */
var Trade = /*#__PURE__*/function () {
  /**
   * Construct a trade by passing in the pre-computed property values
   * @param routes The routes through which the trade occurs
   * @param tradeType The type of trade, exact input or exact output
   */
  function Trade(_ref) {
    var routes = _ref.routes,
      tradeType = _ref.tradeType;
    var inputCurrency = routes[0].inputAmount.currency;
    var outputCurrency = routes[0].outputAmount.currency;
    !routes.every(function (_ref2) {
      var route = _ref2.route;
      return inputCurrency.wrapped.equals(route.input.wrapped);
    }) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INPUT_CURRENCY_MATCH') : invariant(false) : void 0;
    !routes.every(function (_ref3) {
      var route = _ref3.route;
      return outputCurrency.wrapped.equals(route.output.wrapped);
    }) ? process.env.NODE_ENV !== "production" ? invariant(false, 'OUTPUT_CURRENCY_MATCH') : invariant(false) : void 0;
    var numPools = routes.map(function (_ref4) {
      var route = _ref4.route;
      return route.pools.length;
    }).reduce(function (total, cur) {
      return total + cur;
    }, 0);
    var poolAddressSet = new Set();
    for (var _iterator = _createForOfIteratorHelperLoose(routes), _step; !(_step = _iterator()).done;) {
      var route = _step.value.route;
      for (var _iterator2 = _createForOfIteratorHelperLoose(route.pools), _step2; !(_step2 = _iterator2()).done;) {
        var pool = _step2.value;
        poolAddressSet.add(Pool.getAddress(pool.token0, pool.token1));
      }
    }
    !(numPools == poolAddressSet.size) ? process.env.NODE_ENV !== "production" ? invariant(false, 'POOLS_DUPLICATED') : invariant(false) : void 0;
    this.swaps = routes;
    this.tradeType = tradeType;
  }
  /**
   * @deprecated Deprecated in favor of 'swaps' property. If the trade consists of multiple routes
   * this will return an error.
   *
   * When the trade consists of just a single route, this returns the route of the trade,
   * i.e. which pools the trade goes through.
   */
  /**
   * Constructs an exact in trade with the given amount in and route
   * @template TInput The input token, either Ether or an ERC-20
   * @template TOutput The output token, either Ether or an ERC-20
   * @param route The route of the exact in trade
   * @param amountIn The amount being passed in
   * @returns The exact in trade
   */
  Trade.exactIn =
  /*#__PURE__*/
  function () {
    var _exactIn = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee(route, amountIn) {
      return _regeneratorRuntime().wrap(function _callee$(_context) {
        while (1) switch (_context.prev = _context.next) {
          case 0:
            return _context.abrupt("return", Trade.fromRoute(route, amountIn, TradeType.EXACT_INPUT));
          case 1:
          case "end":
            return _context.stop();
        }
      }, _callee);
    }));
    function exactIn(_x, _x2) {
      return _exactIn.apply(this, arguments);
    }
    return exactIn;
  }()
  /**
   * Constructs an exact out trade with the given amount out and route
   * @template TInput The input token, either Ether or an ERC-20
   * @template TOutput The output token, either Ether or an ERC-20
   * @param route The route of the exact out trade
   * @param amountOut The amount returned by the trade
   * @returns The exact out trade
   */
  ;
  Trade.exactOut =
  /*#__PURE__*/
  function () {
    var _exactOut = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee2(route, amountOut) {
      return _regeneratorRuntime().wrap(function _callee2$(_context2) {
        while (1) switch (_context2.prev = _context2.next) {
          case 0:
            return _context2.abrupt("return", Trade.fromRoute(route, amountOut, TradeType.EXACT_OUTPUT));
          case 1:
          case "end":
            return _context2.stop();
        }
      }, _callee2);
    }));
    function exactOut(_x3, _x4) {
      return _exactOut.apply(this, arguments);
    }
    return exactOut;
  }()
  /**
   * Constructs a trade by simulating swaps through the given route
   * @template TInput The input token, either Ether or an ERC-20.
   * @template TOutput The output token, either Ether or an ERC-20.
   * @template TTradeType The type of the trade, either exact in or exact out.
   * @param route route to swap through
   * @param amount the amount specified, either input or output, depending on tradeType
   * @param tradeType whether the trade is an exact input or exact output swap
   * @returns The route
   */
  ;
  Trade.fromRoute =
  /*#__PURE__*/
  function () {
    var _fromRoute = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee3(route, amount, tradeType) {
      var amounts, inputAmount, outputAmount, i, pool, _yield$pool$getOutput, _outputAmount, _i, _pool, _yield$_pool$getInput, _inputAmount;
      return _regeneratorRuntime().wrap(function _callee3$(_context3) {
        while (1) switch (_context3.prev = _context3.next) {
          case 0:
            amounts = new Array(route.tokenPath.length);
            if (!(tradeType === TradeType.EXACT_INPUT)) {
              _context3.next = 19;
              break;
            }
            !amount.currency.equals(route.input) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INPUT') : invariant(false) : void 0;
            amounts[0] = amount.wrapped;
            i = 0;
          case 5:
            if (!(i < route.tokenPath.length - 1)) {
              _context3.next = 15;
              break;
            }
            pool = route.pools[i];
            _context3.next = 9;
            return pool.getOutputAmount(amounts[i]);
          case 9:
            _yield$pool$getOutput = _context3.sent;
            _outputAmount = _yield$pool$getOutput[0];
            amounts[i + 1] = _outputAmount;
          case 12:
            i++;
            _context3.next = 5;
            break;
          case 15:
            inputAmount = CurrencyAmount.fromFractionalAmount(route.input, amount.numerator, amount.denominator);
            outputAmount = CurrencyAmount.fromFractionalAmount(route.output, amounts[amounts.length - 1].numerator, amounts[amounts.length - 1].denominator);
            _context3.next = 34;
            break;
          case 19:
            !amount.currency.equals(route.output) ? process.env.NODE_ENV !== "production" ? invariant(false, 'OUTPUT') : invariant(false) : void 0;
            amounts[amounts.length - 1] = amount.wrapped;
            _i = route.tokenPath.length - 1;
          case 22:
            if (!(_i > 0)) {
              _context3.next = 32;
              break;
            }
            _pool = route.pools[_i - 1];
            _context3.next = 26;
            return _pool.getInputAmount(amounts[_i]);
          case 26:
            _yield$_pool$getInput = _context3.sent;
            _inputAmount = _yield$_pool$getInput[0];
            amounts[_i - 1] = _inputAmount;
          case 29:
            _i--;
            _context3.next = 22;
            break;
          case 32:
            inputAmount = CurrencyAmount.fromFractionalAmount(route.input, amounts[0].numerator, amounts[0].denominator);
            outputAmount = CurrencyAmount.fromFractionalAmount(route.output, amount.numerator, amount.denominator);
          case 34:
            return _context3.abrupt("return", new Trade({
              routes: [{
                inputAmount: inputAmount,
                outputAmount: outputAmount,
                route: route
              }],
              tradeType: tradeType
            }));
          case 35:
          case "end":
            return _context3.stop();
        }
      }, _callee3);
    }));
    function fromRoute(_x5, _x6, _x7) {
      return _fromRoute.apply(this, arguments);
    }
    return fromRoute;
  }()
  /**
   * Constructs a trade from routes by simulating swaps
   *
   * @template TInput The input token, either Ether or an ERC-20.
   * @template TOutput The output token, either Ether or an ERC-20.
   * @template TTradeType The type of the trade, either exact in or exact out.
   * @param routes the routes to swap through and how much of the amount should be routed through each
   * @param tradeType whether the trade is an exact input or exact output swap
   * @returns The trade
   */
  ;
  Trade.fromRoutes =
  /*#__PURE__*/
  function () {
    var _fromRoutes = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee4(routes, tradeType) {
      var populatedRoutes, _iterator3, _step3, _step3$value, route, amount, amounts, inputAmount, outputAmount, i, pool, _yield$pool$getOutput2, _outputAmount2, _i2, _pool2, _yield$_pool2$getInpu, _inputAmount2;
      return _regeneratorRuntime().wrap(function _callee4$(_context4) {
        while (1) switch (_context4.prev = _context4.next) {
          case 0:
            populatedRoutes = [];
            _iterator3 = _createForOfIteratorHelperLoose(routes);
          case 2:
            if ((_step3 = _iterator3()).done) {
              _context4.next = 43;
              break;
            }
            _step3$value = _step3.value, route = _step3$value.route, amount = _step3$value.amount;
            amounts = new Array(route.tokenPath.length);
            inputAmount = void 0;
            outputAmount = void 0;
            if (!(tradeType === TradeType.EXACT_INPUT)) {
              _context4.next = 25;
              break;
            }
            !amount.currency.equals(route.input) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INPUT') : invariant(false) : void 0;
            inputAmount = CurrencyAmount.fromFractionalAmount(route.input, amount.numerator, amount.denominator);
            amounts[0] = CurrencyAmount.fromFractionalAmount(route.input.wrapped, amount.numerator, amount.denominator);
            i = 0;
          case 12:
            if (!(i < route.tokenPath.length - 1)) {
              _context4.next = 22;
              break;
            }
            pool = route.pools[i];
            _context4.next = 16;
            return pool.getOutputAmount(amounts[i]);
          case 16:
            _yield$pool$getOutput2 = _context4.sent;
            _outputAmount2 = _yield$pool$getOutput2[0];
            amounts[i + 1] = _outputAmount2;
          case 19:
            i++;
            _context4.next = 12;
            break;
          case 22:
            outputAmount = CurrencyAmount.fromFractionalAmount(route.output, amounts[amounts.length - 1].numerator, amounts[amounts.length - 1].denominator);
            _context4.next = 40;
            break;
          case 25:
            !amount.currency.equals(route.output) ? process.env.NODE_ENV !== "production" ? invariant(false, 'OUTPUT') : invariant(false) : void 0;
            outputAmount = CurrencyAmount.fromFractionalAmount(route.output, amount.numerator, amount.denominator);
            amounts[amounts.length - 1] = CurrencyAmount.fromFractionalAmount(route.output.wrapped, amount.numerator, amount.denominator);
            _i2 = route.tokenPath.length - 1;
          case 29:
            if (!(_i2 > 0)) {
              _context4.next = 39;
              break;
            }
            _pool2 = route.pools[_i2 - 1];
            _context4.next = 33;
            return _pool2.getInputAmount(amounts[_i2]);
          case 33:
            _yield$_pool2$getInpu = _context4.sent;
            _inputAmount2 = _yield$_pool2$getInpu[0];
            amounts[_i2 - 1] = _inputAmount2;
          case 36:
            _i2--;
            _context4.next = 29;
            break;
          case 39:
            inputAmount = CurrencyAmount.fromFractionalAmount(route.input, amounts[0].numerator, amounts[0].denominator);
          case 40:
            populatedRoutes.push({
              route: route,
              inputAmount: inputAmount,
              outputAmount: outputAmount
            });
          case 41:
            _context4.next = 2;
            break;
          case 43:
            return _context4.abrupt("return", new Trade({
              routes: populatedRoutes,
              tradeType: tradeType
            }));
          case 44:
          case "end":
            return _context4.stop();
        }
      }, _callee4);
    }));
    function fromRoutes(_x8, _x9) {
      return _fromRoutes.apply(this, arguments);
    }
    return fromRoutes;
  }()
  /**
   * Creates a trade without computing the result of swapping through the route. Useful when you have simulated the trade
   * elsewhere and do not have any tick data
   * @template TInput The input token, either Ether or an ERC-20
   * @template TOutput The output token, either Ether or an ERC-20
   * @template TTradeType The type of the trade, either exact in or exact out
   * @param constructorArguments The arguments passed to the trade constructor
   * @returns The unchecked trade
   */
  ;
  Trade.createUncheckedTrade = function createUncheckedTrade(constructorArguments) {
    return new Trade(_extends({}, constructorArguments, {
      routes: [{
        inputAmount: constructorArguments.inputAmount,
        outputAmount: constructorArguments.outputAmount,
        route: constructorArguments.route
      }]
    }));
  }
  /**
   * Creates a trade without computing the result of swapping through the routes. Useful when you have simulated the trade
   * elsewhere and do not have any tick data
   * @template TInput The input token, either Ether or an ERC-20
   * @template TOutput The output token, either Ether or an ERC-20
   * @template TTradeType The type of the trade, either exact in or exact out
   * @param constructorArguments The arguments passed to the trade constructor
   * @returns The unchecked trade
   */;
  Trade.createUncheckedTradeWithMultipleRoutes = function createUncheckedTradeWithMultipleRoutes(constructorArguments) {
    return new Trade(constructorArguments);
  }
  /**
   * Given a list of pools, and a fixed amount in, returns the top `maxNumResults` trades that go from an input token
   * amount to an output token, making at most `maxHops` hops.
   * Note this does not consider aggregation, as routes are linear. It's possible a better route exists by splitting
   * the amount in among multiple routes.
   * @param pools the pools to consider in finding the best trade
   * @param nextAmountIn exact amount of input currency to spend
   * @param currencyOut the desired currency out
   * @param maxNumResults maximum number of results to return
   * @param maxHops maximum number of hops a returned trade can make, e.g. 1 hop goes through a single pool
   * @param currentPools used in recursion; the current list of pools
   * @param currencyAmountIn used in recursion; the original value of the currencyAmountIn parameter
   * @param bestTrades used in recursion; the current list of best trades
   * @returns The exact in trade
   */;
  Trade.bestTradeExactIn =
  /*#__PURE__*/
  function () {
    var _bestTradeExactIn = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee5(pools, currencyAmountIn, currencyOut, _temp,
    // used in recursion.
    currentPools, nextAmountIn, bestTrades) {
      var _ref5, _ref5$maxNumResults, maxNumResults, _ref5$maxHops, maxHops, amountIn, tokenOut, i, pool, amountOut, _yield$pool$getOutput3, error, poolsExcludingThisPool;
      return _regeneratorRuntime().wrap(function _callee5$(_context5) {
        while (1) switch (_context5.prev = _context5.next) {
          case 0:
            _ref5 = _temp === void 0 ? {} : _temp, _ref5$maxNumResults = _ref5.maxNumResults, maxNumResults = _ref5$maxNumResults === void 0 ? 3 : _ref5$maxNumResults, _ref5$maxHops = _ref5.maxHops, maxHops = _ref5$maxHops === void 0 ? 3 : _ref5$maxHops;
            if (currentPools === void 0) {
              currentPools = [];
            }
            if (nextAmountIn === void 0) {
              nextAmountIn = currencyAmountIn;
            }
            if (bestTrades === void 0) {
              bestTrades = [];
            }
            !(pools.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'POOLS') : invariant(false) : void 0;
            !(maxHops > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'MAX_HOPS') : invariant(false) : void 0;
            !(currencyAmountIn === nextAmountIn || currentPools.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INVALID_RECURSION') : invariant(false) : void 0;
            amountIn = nextAmountIn.wrapped;
            tokenOut = currencyOut.wrapped;
            i = 0;
          case 10:
            if (!(i < pools.length)) {
              _context5.next = 46;
              break;
            }
            pool = pools[i]; // pool irrelevant
            if (!(!pool.token0.equals(amountIn.currency) && !pool.token1.equals(amountIn.currency))) {
              _context5.next = 14;
              break;
            }
            return _context5.abrupt("continue", 43);
          case 14:
            amountOut = void 0;
            _context5.prev = 15;
            _context5.next = 18;
            return pool.getOutputAmount(amountIn);
          case 18:
            _yield$pool$getOutput3 = _context5.sent;
            amountOut = _yield$pool$getOutput3[0];
            _context5.next = 28;
            break;
          case 22:
            _context5.prev = 22;
            _context5.t0 = _context5["catch"](15);
            error = _context5.t0; // input too low
            if (!error.isInsufficientInputAmountError) {
              _context5.next = 27;
              break;
            }
            return _context5.abrupt("continue", 43);
          case 27:
            throw error;
          case 28:
            if (!(amountOut.currency.isToken && amountOut.currency.equals(tokenOut))) {
              _context5.next = 39;
              break;
            }
            _context5.t1 = sortedInsert;
            _context5.t2 = bestTrades;
            _context5.next = 33;
            return Trade.fromRoute(new Route([].concat(currentPools, [pool]), currencyAmountIn.currency, currencyOut), currencyAmountIn, TradeType.EXACT_INPUT);
          case 33:
            _context5.t3 = _context5.sent;
            _context5.t4 = maxNumResults;
            _context5.t5 = tradeComparator;
            (0, _context5.t1)(_context5.t2, _context5.t3, _context5.t4, _context5.t5);
            _context5.next = 43;
            break;
          case 39:
            if (!(maxHops > 1 && pools.length > 1)) {
              _context5.next = 43;
              break;
            }
            poolsExcludingThisPool = pools.slice(0, i).concat(pools.slice(i + 1, pools.length)); // otherwise, consider all the other paths that lead from this token as long as we have not exceeded maxHops
            _context5.next = 43;
            return Trade.bestTradeExactIn(poolsExcludingThisPool, currencyAmountIn, currencyOut, {
              maxNumResults: maxNumResults,
              maxHops: maxHops - 1
            }, [].concat(currentPools, [pool]), amountOut, bestTrades);
          case 43:
            i++;
            _context5.next = 10;
            break;
          case 46:
            return _context5.abrupt("return", bestTrades);
          case 47:
          case "end":
            return _context5.stop();
        }
      }, _callee5, null, [[15, 22]]);
    }));
    function bestTradeExactIn(_x10, _x11, _x12, _x13, _x14, _x15, _x16) {
      return _bestTradeExactIn.apply(this, arguments);
    }
    return bestTradeExactIn;
  }()
  /**
   * similar to the above method but instead targets a fixed output amount
   * given a list of pools, and a fixed amount out, returns the top `maxNumResults` trades that go from an input token
   * to an output token amount, making at most `maxHops` hops
   * note this does not consider aggregation, as routes are linear. it's possible a better route exists by splitting
   * the amount in among multiple routes.
   * @param pools the pools to consider in finding the best trade
   * @param currencyIn the currency to spend
   * @param currencyAmountOut the desired currency amount out
   * @param nextAmountOut the exact amount of currency out
   * @param maxNumResults maximum number of results to return
   * @param maxHops maximum number of hops a returned trade can make, e.g. 1 hop goes through a single pool
   * @param currentPools used in recursion; the current list of pools
   * @param bestTrades used in recursion; the current list of best trades
   * @returns The exact out trade
   */
  ;
  Trade.bestTradeExactOut =
  /*#__PURE__*/
  function () {
    var _bestTradeExactOut = /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee6(pools, currencyIn, currencyAmountOut, _temp2,
    // used in recursion.
    currentPools, nextAmountOut, bestTrades) {
      var _ref6, _ref6$maxNumResults, maxNumResults, _ref6$maxHops, maxHops, amountOut, tokenIn, i, pool, amountIn, _yield$pool$getInputA, error, poolsExcludingThisPool;
      return _regeneratorRuntime().wrap(function _callee6$(_context6) {
        while (1) switch (_context6.prev = _context6.next) {
          case 0:
            _ref6 = _temp2 === void 0 ? {} : _temp2, _ref6$maxNumResults = _ref6.maxNumResults, maxNumResults = _ref6$maxNumResults === void 0 ? 3 : _ref6$maxNumResults, _ref6$maxHops = _ref6.maxHops, maxHops = _ref6$maxHops === void 0 ? 3 : _ref6$maxHops;
            if (currentPools === void 0) {
              currentPools = [];
            }
            if (nextAmountOut === void 0) {
              nextAmountOut = currencyAmountOut;
            }
            if (bestTrades === void 0) {
              bestTrades = [];
            }
            !(pools.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'POOLS') : invariant(false) : void 0;
            !(maxHops > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'MAX_HOPS') : invariant(false) : void 0;
            !(currencyAmountOut === nextAmountOut || currentPools.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'INVALID_RECURSION') : invariant(false) : void 0;
            amountOut = nextAmountOut.wrapped;
            tokenIn = currencyIn.wrapped;
            i = 0;
          case 10:
            if (!(i < pools.length)) {
              _context6.next = 46;
              break;
            }
            pool = pools[i]; // pool irrelevant
            if (!(!pool.token0.equals(amountOut.currency) && !pool.token1.equals(amountOut.currency))) {
              _context6.next = 14;
              break;
            }
            return _context6.abrupt("continue", 43);
          case 14:
            amountIn = void 0;
            _context6.prev = 15;
            _context6.next = 18;
            return pool.getInputAmount(amountOut);
          case 18:
            _yield$pool$getInputA = _context6.sent;
            amountIn = _yield$pool$getInputA[0];
            _context6.next = 28;
            break;
          case 22:
            _context6.prev = 22;
            _context6.t0 = _context6["catch"](15);
            // not enough liquidity in this pool
            error = _context6.t0;
            if (!error.isInsufficientReservesError) {
              _context6.next = 27;
              break;
            }
            return _context6.abrupt("continue", 43);
          case 27:
            throw error;
          case 28:
            if (!amountIn.currency.equals(tokenIn)) {
              _context6.next = 39;
              break;
            }
            _context6.t1 = sortedInsert;
            _context6.t2 = bestTrades;
            _context6.next = 33;
            return Trade.fromRoute(new Route([pool].concat(currentPools), currencyIn, currencyAmountOut.currency), currencyAmountOut, TradeType.EXACT_OUTPUT);
          case 33:
            _context6.t3 = _context6.sent;
            _context6.t4 = maxNumResults;
            _context6.t5 = tradeComparator;
            (0, _context6.t1)(_context6.t2, _context6.t3, _context6.t4, _context6.t5);
            _context6.next = 43;
            break;
          case 39:
            if (!(maxHops > 1 && pools.length > 1)) {
              _context6.next = 43;
              break;
            }
            poolsExcludingThisPool = pools.slice(0, i).concat(pools.slice(i + 1, pools.length)); // otherwise, consider all the other paths that arrive at this token as long as we have not exceeded maxHops
            _context6.next = 43;
            return Trade.bestTradeExactOut(poolsExcludingThisPool, currencyIn, currencyAmountOut, {
              maxNumResults: maxNumResults,
              maxHops: maxHops - 1
            }, [pool].concat(currentPools), amountIn, bestTrades);
          case 43:
            i++;
            _context6.next = 10;
            break;
          case 46:
            return _context6.abrupt("return", bestTrades);
          case 47:
          case "end":
            return _context6.stop();
        }
      }, _callee6, null, [[15, 22]]);
    }));
    function bestTradeExactOut(_x17, _x18, _x19, _x20, _x21, _x22, _x23) {
      return _bestTradeExactOut.apply(this, arguments);
    }
    return bestTradeExactOut;
  }()
  /**
   * Get the minimum amount that must be received from this trade for the given slippage tolerance
   * @param slippageTolerance The tolerance of unfavorable slippage from the execution price of this trade
   * @returns The amount out
   */
  ;
  var _proto = Trade.prototype;
  _proto.minimumAmountOut = function minimumAmountOut(slippageTolerance, amountOut) {
    if (amountOut === void 0) {
      amountOut = this.outputAmount;
    }
    !!slippageTolerance.lessThan(ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'SLIPPAGE_TOLERANCE') : invariant(false) : void 0;
    if (this.tradeType === TradeType.EXACT_OUTPUT) {
      return amountOut;
    } else {
      var slippageAdjustedAmountOut = new Fraction(ONE).add(slippageTolerance).invert().multiply(amountOut.quotient).quotient;
      return CurrencyAmount.fromRawAmount(amountOut.currency, slippageAdjustedAmountOut);
    }
  }
  /**
   * Get the maximum amount in that can be spent via this trade for the given slippage tolerance
   * @param slippageTolerance The tolerance of unfavorable slippage from the execution price of this trade
   * @returns The amount in
   */;
  _proto.maximumAmountIn = function maximumAmountIn(slippageTolerance, amountIn) {
    if (amountIn === void 0) {
      amountIn = this.inputAmount;
    }
    !!slippageTolerance.lessThan(ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'SLIPPAGE_TOLERANCE') : invariant(false) : void 0;
    if (this.tradeType === TradeType.EXACT_INPUT) {
      return amountIn;
    } else {
      var slippageAdjustedAmountIn = new Fraction(ONE).add(slippageTolerance).multiply(amountIn.quotient).quotient;
      return CurrencyAmount.fromRawAmount(amountIn.currency, slippageAdjustedAmountIn);
    }
  }
  /**
   * Return the execution price after accounting for slippage tolerance
   * @param slippageTolerance the allowed tolerated slippage
   * @returns The execution price
   */;
  _proto.worstExecutionPrice = function worstExecutionPrice(slippageTolerance) {
    return new Price(this.inputAmount.currency, this.outputAmount.currency, this.maximumAmountIn(slippageTolerance).quotient, this.minimumAmountOut(slippageTolerance).quotient);
  };
  _createClass(Trade, [{
    key: "route",
    get: function get() {
      !(this.swaps.length == 1) ? process.env.NODE_ENV !== "production" ? invariant(false, 'MULTIPLE_ROUTES') : invariant(false) : void 0;
      return this.swaps[0].route;
    }
    /**
     * The input amount for the trade assuming no slippage.
     */
  }, {
    key: "inputAmount",
    get: function get() {
      if (this._inputAmount) {
        return this._inputAmount;
      }
      var inputCurrency = this.swaps[0].inputAmount.currency;
      var totalInputFromRoutes = this.swaps.map(function (_ref7) {
        var inputAmount = _ref7.inputAmount;
        return inputAmount;
      }).reduce(function (total, cur) {
        return total.add(cur);
      }, CurrencyAmount.fromRawAmount(inputCurrency, 0));
      this._inputAmount = totalInputFromRoutes;
      return this._inputAmount;
    }
    /**
     * The output amount for the trade assuming no slippage.
     */
  }, {
    key: "outputAmount",
    get: function get() {
      if (this._outputAmount) {
        return this._outputAmount;
      }
      var outputCurrency = this.swaps[0].outputAmount.currency;
      var totalOutputFromRoutes = this.swaps.map(function (_ref8) {
        var outputAmount = _ref8.outputAmount;
        return outputAmount;
      }).reduce(function (total, cur) {
        return total.add(cur);
      }, CurrencyAmount.fromRawAmount(outputCurrency, 0));
      this._outputAmount = totalOutputFromRoutes;
      return this._outputAmount;
    }
    /**
     * The price expressed in terms of output amount/input amount.
     */
  }, {
    key: "executionPrice",
    get: function get() {
      var _this$_executionPrice;
      return (_this$_executionPrice = this._executionPrice) != null ? _this$_executionPrice : this._executionPrice = new Price(this.inputAmount.currency, this.outputAmount.currency, this.inputAmount.quotient, this.outputAmount.quotient);
    }
    /**
     * Returns the percent difference between the route's mid price and the price impact
     */
  }, {
    key: "priceImpact",
    get: function get() {
      if (this._priceImpact) {
        return this._priceImpact;
      }
      var spotOutputAmount = CurrencyAmount.fromRawAmount(this.outputAmount.currency, 0);
      for (var _iterator4 = _createForOfIteratorHelperLoose(this.swaps), _step4; !(_step4 = _iterator4()).done;) {
        var _step4$value = _step4.value,
          route = _step4$value.route,
          inputAmount = _step4$value.inputAmount;
        var midPrice = route.midPrice;
        spotOutputAmount = spotOutputAmount.add(midPrice.quote(inputAmount));
      }
      var priceImpact = spotOutputAmount.subtract(this.outputAmount).divide(spotOutputAmount);
      this._priceImpact = new Percent(priceImpact.numerator, priceImpact.denominator);
      return this._priceImpact;
    }
  }]);
  return Trade;
}();

var Rounding;
(function (Rounding) {
  Rounding[Rounding["ROUND_DOWN"] = 0] = "ROUND_DOWN";
  Rounding[Rounding["ROUND_HALF_UP"] = 1] = "ROUND_HALF_UP";
  Rounding[Rounding["ROUND_UP"] = 2] = "ROUND_UP";
})(Rounding || (Rounding = {}));

var _toSignificantRoundin, _toFixedRounding;
var Decimal = /*#__PURE__*/toFormat(_Decimal);
var Big = /*#__PURE__*/toFormat(_Big);
var toSignificantRounding = (_toSignificantRoundin = {}, _toSignificantRoundin[Rounding.ROUND_DOWN] = Decimal.ROUND_DOWN, _toSignificantRoundin[Rounding.ROUND_HALF_UP] = Decimal.ROUND_HALF_UP, _toSignificantRoundin[Rounding.ROUND_UP] = Decimal.ROUND_UP, _toSignificantRoundin);
var toFixedRounding = (_toFixedRounding = {}, _toFixedRounding[Rounding.ROUND_DOWN] = 0, _toFixedRounding[Rounding.ROUND_HALF_UP] = 1, _toFixedRounding[Rounding.ROUND_UP] = 3, _toFixedRounding);
var Fraction = /*#__PURE__*/function () {
  function Fraction(numerator, denominator) {
    if (denominator === void 0) {
      denominator = JSBI.BigInt(1);
    }
    this.numerator = JSBI.BigInt(numerator);
    this.denominator = JSBI.BigInt(denominator);
  }
  Fraction.tryParseFraction = function tryParseFraction(fractionish) {
    if (fractionish instanceof JSBI || typeof fractionish === 'number' || typeof fractionish === 'string') return new Fraction(fractionish);
    if ('numerator' in fractionish && 'denominator' in fractionish) return fractionish;
    throw new Error('Could not parse fraction');
  }
  // performs floor division
  ;
  var _proto = Fraction.prototype;
  _proto.invert = function invert() {
    return new Fraction(this.denominator, this.numerator);
  };
  _proto.add = function add(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    if (JSBI.equal(this.denominator, otherParsed.denominator)) {
      return new Fraction(JSBI.add(this.numerator, otherParsed.numerator), this.denominator);
    }
    return new Fraction(JSBI.add(JSBI.multiply(this.numerator, otherParsed.denominator), JSBI.multiply(otherParsed.numerator, this.denominator)), JSBI.multiply(this.denominator, otherParsed.denominator));
  };
  _proto.subtract = function subtract(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    if (JSBI.equal(this.denominator, otherParsed.denominator)) {
      return new Fraction(JSBI.subtract(this.numerator, otherParsed.numerator), this.denominator);
    }
    return new Fraction(JSBI.subtract(JSBI.multiply(this.numerator, otherParsed.denominator), JSBI.multiply(otherParsed.numerator, this.denominator)), JSBI.multiply(this.denominator, otherParsed.denominator));
  };
  _proto.lessThan = function lessThan(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    return JSBI.lessThan(JSBI.multiply(this.numerator, otherParsed.denominator), JSBI.multiply(otherParsed.numerator, this.denominator));
  };
  _proto.equalTo = function equalTo(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    return JSBI.equal(JSBI.multiply(this.numerator, otherParsed.denominator), JSBI.multiply(otherParsed.numerator, this.denominator));
  };
  _proto.greaterThan = function greaterThan(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    return JSBI.greaterThan(JSBI.multiply(this.numerator, otherParsed.denominator), JSBI.multiply(otherParsed.numerator, this.denominator));
  };
  _proto.multiply = function multiply(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    return new Fraction(JSBI.multiply(this.numerator, otherParsed.numerator), JSBI.multiply(this.denominator, otherParsed.denominator));
  };
  _proto.divide = function divide(other) {
    var otherParsed = Fraction.tryParseFraction(other);
    return new Fraction(JSBI.multiply(this.numerator, otherParsed.denominator), JSBI.multiply(this.denominator, otherParsed.numerator));
  };
  _proto.toSignificant = function toSignificant(significantDigits, format, rounding) {
    if (format === void 0) {
      format = {
        groupSeparator: ''
      };
    }
    if (rounding === void 0) {
      rounding = Rounding.ROUND_HALF_UP;
    }
    !Number.isInteger(significantDigits) ? process.env.NODE_ENV !== "production" ? invariant(false, significantDigits + " is not an integer.") : invariant(false) : void 0;
    !(significantDigits > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, significantDigits + " is not positive.") : invariant(false) : void 0;
    Decimal.set({
      precision: significantDigits + 1,
      rounding: toSignificantRounding[rounding]
    });
    var quotient = new Decimal(this.numerator.toString()).div(this.denominator.toString()).toSignificantDigits(significantDigits);
    return quotient.toFormat(quotient.decimalPlaces(), format);
  };
  _proto.toFixed = function toFixed(decimalPlaces, format, rounding) {
    if (format === void 0) {
      format = {
        groupSeparator: ''
      };
    }
    if (rounding === void 0) {
      rounding = Rounding.ROUND_HALF_UP;
    }
    !Number.isInteger(decimalPlaces) ? process.env.NODE_ENV !== "production" ? invariant(false, decimalPlaces + " is not an integer.") : invariant(false) : void 0;
    !(decimalPlaces >= 0) ? process.env.NODE_ENV !== "production" ? invariant(false, decimalPlaces + " is negative.") : invariant(false) : void 0;
    Big.DP = decimalPlaces;
    Big.RM = toFixedRounding[rounding];
    return new Big(this.numerator.toString()).div(this.denominator.toString()).toFormat(decimalPlaces, format);
  }
  /**
   * Helper method for converting any super class back to a fraction
   */;
  _createClass(Fraction, [{
    key: "quotient",
    get: function get() {
      return JSBI.divide(this.numerator, this.denominator);
    }
    // remainder after floor division
  }, {
    key: "remainder",
    get: function get() {
      return new Fraction(JSBI.remainder(this.numerator, this.denominator), this.denominator);
    }
  }, {
    key: "asFraction",
    get: function get() {
      return new Fraction(this.numerator, this.denominator);
    }
  }]);
  return Fraction;
}();

var Big$1 = /*#__PURE__*/toFormat(_Big);
var CurrencyAmount = /*#__PURE__*/function (_Fraction) {
  _inheritsLoose(CurrencyAmount, _Fraction);
  function CurrencyAmount(currency, numerator, denominator) {
    var _this;
    _this = _Fraction.call(this, numerator, denominator) || this;
    !JSBI.lessThanOrEqual(_this.quotient, MaxUint256) ? process.env.NODE_ENV !== "production" ? invariant(false, 'AMOUNT') : invariant(false) : void 0;
    _this.currency = currency;
    _this.decimalScale = JSBI.exponentiate(JSBI.BigInt(10), JSBI.BigInt(currency.decimals));
    return _this;
  }
  /**
   * Returns a new currency amount instance from the unitless amount of token, i.e. the raw amount
   * @param currency the currency in the amount
   * @param rawAmount the raw token or ether amount
   */
  CurrencyAmount.fromRawAmount = function fromRawAmount(currency, rawAmount) {
    return new CurrencyAmount(currency, rawAmount);
  }
  /**
   * Construct a currency amount with a denominator that is not equal to 1
   * @param currency the currency
   * @param numerator the numerator of the fractional token amount
   * @param denominator the denominator of the fractional token amount
   */;
  CurrencyAmount.fromFractionalAmount = function fromFractionalAmount(currency, numerator, denominator) {
    return new CurrencyAmount(currency, numerator, denominator);
  };
  var _proto = CurrencyAmount.prototype;
  _proto.add = function add(other) {
    !this.currency.equals(other.currency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'CURRENCY') : invariant(false) : void 0;
    var added = _Fraction.prototype.add.call(this, other);
    return CurrencyAmount.fromFractionalAmount(this.currency, added.numerator, added.denominator);
  };
  _proto.subtract = function subtract(other) {
    !this.currency.equals(other.currency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'CURRENCY') : invariant(false) : void 0;
    var subtracted = _Fraction.prototype.subtract.call(this, other);
    return CurrencyAmount.fromFractionalAmount(this.currency, subtracted.numerator, subtracted.denominator);
  };
  _proto.multiply = function multiply(other) {
    var multiplied = _Fraction.prototype.multiply.call(this, other);
    return CurrencyAmount.fromFractionalAmount(this.currency, multiplied.numerator, multiplied.denominator);
  };
  _proto.divide = function divide(other) {
    var divided = _Fraction.prototype.divide.call(this, other);
    return CurrencyAmount.fromFractionalAmount(this.currency, divided.numerator, divided.denominator);
  };
  _proto.toSignificant = function toSignificant(significantDigits, format, rounding) {
    if (significantDigits === void 0) {
      significantDigits = 6;
    }
    if (rounding === void 0) {
      rounding = Rounding.ROUND_DOWN;
    }
    return _Fraction.prototype.divide.call(this, this.decimalScale).toSignificant(significantDigits, format, rounding);
  };
  _proto.toFixed = function toFixed(decimalPlaces, format, rounding) {
    if (decimalPlaces === void 0) {
      decimalPlaces = this.currency.decimals;
    }
    if (rounding === void 0) {
      rounding = Rounding.ROUND_DOWN;
    }
    !(decimalPlaces <= this.currency.decimals) ? process.env.NODE_ENV !== "production" ? invariant(false, 'DECIMALS') : invariant(false) : void 0;
    return _Fraction.prototype.divide.call(this, this.decimalScale).toFixed(decimalPlaces, format, rounding);
  };
  _proto.toExact = function toExact(format) {
    if (format === void 0) {
      format = {
        groupSeparator: ''
      };
    }
    Big$1.DP = this.currency.decimals;
    return new Big$1(this.quotient.toString()).div(this.decimalScale.toString()).toFormat(format);
  };
  _createClass(CurrencyAmount, [{
    key: "wrapped",
    get: function get() {
      if (this.currency.isToken) return this;
      return CurrencyAmount.fromFractionalAmount(this.currency.wrapped, this.numerator, this.denominator);
    }
  }]);
  return CurrencyAmount;
}(Fraction);

var Price = /*#__PURE__*/function (_Fraction) {
  _inheritsLoose(Price, _Fraction);
  /**
   * Construct a price, either with the base and quote currency amount, or the
   * @param args
   */
  function Price() {
    var _this;
    var baseCurrency, quoteCurrency, denominator, numerator;
    for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }
    if (args.length === 4) {
      baseCurrency = args[0];
      quoteCurrency = args[1];
      denominator = args[2];
      numerator = args[3];
    } else {
      var result = args[0].quoteAmount.divide(args[0].baseAmount);
      var _ref = [args[0].baseAmount.currency, args[0].quoteAmount.currency, result.denominator, result.numerator];
      baseCurrency = _ref[0];
      quoteCurrency = _ref[1];
      denominator = _ref[2];
      numerator = _ref[3];
    }
    _this = _Fraction.call(this, numerator, denominator) || this;
    _this.baseCurrency = baseCurrency;
    _this.quoteCurrency = quoteCurrency;
    _this.scalar = new Fraction(JSBI.exponentiate(JSBI.BigInt(10), JSBI.BigInt(baseCurrency.decimals)), JSBI.exponentiate(JSBI.BigInt(10), JSBI.BigInt(quoteCurrency.decimals)));
    return _this;
  }
  /**
   * Flip the price, switching the base and quote currency
   */
  var _proto = Price.prototype;
  _proto.invert = function invert() {
    return new Price(this.quoteCurrency, this.baseCurrency, this.numerator, this.denominator);
  }
  /**
   * Multiply the price by another price, returning a new price. The other price must have the same base currency as this price's quote currency
   * @param other the other price
   */;
  _proto.multiply = function multiply(other) {
    !this.quoteCurrency.equals(other.baseCurrency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN') : invariant(false) : void 0;
    var fraction = _Fraction.prototype.multiply.call(this, other);
    return new Price(this.baseCurrency, other.quoteCurrency, fraction.denominator, fraction.numerator);
  }
  /**
   * Return the amount of quote currency corresponding to a given amount of the base currency
   * @param currencyAmount the amount of base currency to quote against the price
   */;
  _proto.quote = function quote(currencyAmount) {
    !currencyAmount.currency.equals(this.baseCurrency) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN') : invariant(false) : void 0;
    var result = _Fraction.prototype.multiply.call(this, currencyAmount);
    return CurrencyAmount.fromFractionalAmount(this.quoteCurrency, result.numerator, result.denominator);
  }
  /**
   * Get the value scaled by decimals for formatting
   * @private
   */;
  _proto.toSignificant = function toSignificant(significantDigits, format, rounding) {
    if (significantDigits === void 0) {
      significantDigits = 6;
    }
    return this.adjustedForDecimals.toSignificant(significantDigits, format, rounding);
  };
  _proto.toFixed = function toFixed(decimalPlaces, format, rounding) {
    if (decimalPlaces === void 0) {
      decimalPlaces = 4;
    }
    return this.adjustedForDecimals.toFixed(decimalPlaces, format, rounding);
  };
  _createClass(Price, [{
    key: "adjustedForDecimals",
    get: function get() {
      return _Fraction.prototype.multiply.call(this, this.scalar);
    }
  }]);
  return Price;
}(Fraction);

var ONE_HUNDRED = /*#__PURE__*/new Fraction( /*#__PURE__*/JSBI.BigInt(100));
/**
 * Converts a fraction to a percent
 * @param fraction the fraction to convert
 */
function toPercent(fraction) {
  return new Percent(fraction.numerator, fraction.denominator);
}
var Percent = /*#__PURE__*/function (_Fraction) {
  _inheritsLoose(Percent, _Fraction);
  function Percent(numerator, denominator) {
    var _this;
    if (denominator === void 0) {
      denominator = JSBI.BigInt(1);
    }
    _this = _Fraction.call(this, numerator, denominator) || this;
    /**
     * This boolean prevents a fraction from being interpreted as a Percent
     */
    _this.isPercent = true;
    return _this;
  }
  var _proto = Percent.prototype;
  _proto.add = function add(other) {
    return toPercent(_Fraction.prototype.add.call(this, other));
  };
  _proto.subtract = function subtract(other) {
    return toPercent(_Fraction.prototype.subtract.call(this, other));
  };
  _proto.multiply = function multiply(other) {
    return toPercent(_Fraction.prototype.multiply.call(this, other));
  };
  _proto.divide = function divide(other) {
    return toPercent(_Fraction.prototype.divide.call(this, other));
  };
  _proto.toSignificant = function toSignificant(significantDigits, format, rounding) {
    if (significantDigits === void 0) {
      significantDigits = 5;
    }
    return _Fraction.prototype.multiply.call(this, ONE_HUNDRED).toSignificant(significantDigits, format, rounding);
  };
  _proto.toFixed = function toFixed(decimalPlaces, format, rounding) {
    if (decimalPlaces === void 0) {
      decimalPlaces = 2;
    }
    return _Fraction.prototype.multiply.call(this, ONE_HUNDRED).toFixed(decimalPlaces, format, rounding);
  };
  return Percent;
}(Fraction);

/**
 * Represents the native currency of the chain on which it resides, e.g.
 */
var NativeCurrency = /*#__PURE__*/function (_AbstractCurrency) {
  _inheritsLoose(NativeCurrency, _AbstractCurrency);
  function NativeCurrency() {
    var _this;
    _this = _AbstractCurrency.apply(this, arguments) || this;
    _this.isNative = true;
    _this.isToken = false;
    _this.isBoosted = false;
    return _this;
  }
  return NativeCurrency;
}(AbstractCurrency);

/**
 * Native is the main usage of a 'native' currency
 */
var Native = /*#__PURE__*/function (_NativeCurrency) {
  _inheritsLoose(Native, _NativeCurrency);
  function Native(chainId, symbol, name) {
    return _NativeCurrency.call(this, chainId, 18, symbol, name) || this;
  }
  Native.onChain = function onChain(chainId, symbol, name) {
    var _this$_naitveCache$ch;
    return (_this$_naitveCache$ch = this._naitveCache[chainId]) != null ? _this$_naitveCache$ch : this._naitveCache[chainId] = new Native(chainId, symbol, name);
  };
  var _proto = Native.prototype;
  _proto.equals = function equals(other) {
    return other.isNative && other.chainId === this.chainId;
  };
  _createClass(Native, [{
    key: "wrapped",
    get: function get() {
      var wnative = WNATIVE[this.chainId];
      !!!wnative ? process.env.NODE_ENV !== "production" ? invariant(false, 'WRAPPED') : invariant(false) : void 0;
      return wnative;
    }
  }]);
  return Native;
}(NativeCurrency);
Native._naitveCache = {};

var ExtendedNative = /*#__PURE__*/function (_Native) {
  _inheritsLoose(ExtendedNative, _Native);
  function ExtendedNative() {
    return _Native.apply(this, arguments) || this;
  }
  ExtendedNative.onChain = function onChain(chainId, symbol, name) {
    var _this$_cachedNative$c;
    return (_this$_cachedNative$c = this._cachedNative[chainId]) != null ? _this$_cachedNative$c : this._cachedNative[chainId] = new ExtendedNative(chainId, symbol, name);
  };
  _createClass(ExtendedNative, [{
    key: "wrapped",
    get: function get() {
      return WNATIVE[this.chainId];
    }
  }]);
  return ExtendedNative;
}(Native);
ExtendedNative._cachedNative = {};

/**
 * Represents an ERC4626-wrapped token ("boosted token") that corresponds
 * to an underlying ERC20 token and adds vault-like behavior.
 */
var BoostedToken = /*#__PURE__*/function (_AbstractCurrency) {
  _inheritsLoose(BoostedToken, _AbstractCurrency);
  function BoostedToken(chainId, address, decimals, symbol, name, underlying) {
    var _this;
    _this = _AbstractCurrency.call(this, chainId, decimals, symbol, name) || this;
    /** Flag to identify boosted tokens in runtime type checks */
    _this.isBoosted = true;
    _this.isToken = true;
    _this.isNative = false;
    _this.chainId = chainId;
    _this.address = validateAndParseAddress(address);
    _this.underlying = underlying;
    return _this;
  }
  /**
   * Returns the underlying (unwrapped) ERC20 token.
   */
  var _proto = BoostedToken.prototype;
  /**
   * Boosted tokens are not considered equal to their underlying asset,
   * but may share metadata (symbol/name) for UI display purposes.
   */
  _proto.equals = function equals(other) {
    if (other.isBoosted) {
      return this.chainId === other.chainId && this.address === other.address && this.underlying.equals(other.underlying);
    }
    return false;
  }
  /**
   * Returns true if the address of this token sorts before the address of the other token
   * @param other other token to compare
   * @throws if the tokens have the same address
   * @throws if the tokens are on different chains
   */;
  _proto.sortsBefore = function sortsBefore(other) {
    !(this.chainId === other.chainId) ? process.env.NODE_ENV !== "production" ? invariant(false, 'CHAIN_IDS') : invariant(false) : void 0;
    !(this.address !== other.address) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ADDRESSES') : invariant(false) : void 0;
    return this.address.toLowerCase() < other.address.toLowerCase();
  };
  _createClass(BoostedToken, [{
    key: "unwrapped",
    get: function get() {
      return this.underlying;
    }
    /**
     * For BoostedToken, wrapped should return itself (not the underlying).
     * This allows proper routing through boosted pools.
     */
  }, {
    key: "wrapped",
    get: function get() {
      return this;
    }
  }]);
  return BoostedToken;
}(AbstractCurrency);

/**
 * Type of operation in a boosted route step
 */
var BoostedRouteStepType;
(function (BoostedRouteStepType) {
  /** ERC4626 deposit: underlying → shares */
  BoostedRouteStepType["WRAP"] = "WRAP";
  /** ERC4626 redeem: shares → underlying */
  BoostedRouteStepType["UNWRAP"] = "UNWRAP";
  /** AMM swap through pool */
  BoostedRouteStepType["SWAP"] = "SWAP";
})(BoostedRouteStepType || (BoostedRouteStepType = {}));
/**
 * Represents a list of pools through which a boosted swap can occur
 * Supports wrapping/unwrapping logic for BoostedTokens (ERC4626)
 */
var BoostedRoute = /*#__PURE__*/function () {
  function BoostedRoute(pools, input, output) {
    this.isBoosted = true;
    this._midPrice = null;
    var wrappedInput = input.wrapped;
    var wrappedOutput = output.wrapped;
    // ═══════════════════════════════════════════════════════════
    // CASE 1: DIRECT WRAP (pools.length === 0)
    // Underlying → BoostedToken (e.g., WETH → mwETH)
    // ═══════════════════════════════════════════════════════════
    if (pools.length === 0 && wrappedOutput.isBoosted && !wrappedInput.isBoosted) {
      !wrappedOutput.underlying.equals(wrappedInput) ? process.env.NODE_ENV !== "production" ? invariant(false, 'DIRECT_WRAP: output must wrap input') : invariant(false) : void 0;
      this.pools = pools;
      this.tokenPath = [wrappedInput, wrappedOutput];
      this.steps = [{
        type: BoostedRouteStepType.WRAP,
        tokenIn: wrappedInput,
        tokenOut: wrappedOutput
      }];
      this.input = input;
      this.output = output;
      return;
    }
    // ═══════════════════════════════════════════════════════════
    // CASE 2: DIRECT UNWRAP (pools.length === 0)
    // BoostedToken → Underlying (e.g., mwETH → WETH)
    // ═══════════════════════════════════════════════════════════
    if (pools.length === 0 && wrappedInput.isBoosted && !wrappedOutput.isBoosted) {
      !wrappedInput.underlying.equals(wrappedOutput) ? process.env.NODE_ENV !== "production" ? invariant(false, 'DIRECT_UNWRAP: input must unwrap to output') : invariant(false) : void 0;
      this.pools = pools;
      this.tokenPath = [wrappedInput, wrappedOutput];
      this.steps = [{
        type: BoostedRouteStepType.UNWRAP,
        tokenIn: wrappedInput,
        tokenOut: wrappedOutput
      }];
      this.input = input;
      this.output = output;
      return;
    }
    // ═══════════════════════════════════════════════════════════
    // CASE 3: BOOSTED ROUTE WITH POOLS
    // Input/Output through boosted pools with wrap/unwrap steps
    // ═══════════════════════════════════════════════════════════
    !(pools.length > 0) ? process.env.NODE_ENV !== "production" ? invariant(false, 'POOLS: routes with pools must have at least one pool') : invariant(false) : void 0;
    var chainId = pools[0].chainId;
    var allOnSameChain = pools.every(function (pool) {
      return pool.chainId === chainId;
    });
    !allOnSameChain ? process.env.NODE_ENV !== "production" ? invariant(false, 'CHAIN_IDS') : invariant(false) : void 0;
    var tokenPath = [];
    var steps = [];
    var currentToken = wrappedInput;
    // Start with input token
    tokenPath.push(currentToken);
    // Build path through pools with wrap/unwrap between them
    var _loop = function _loop() {
      var pool = pools[i];
      // Check if current token exists in pool
      var isToken0 = currentToken.equals(pool.token0);
      var isToken1 = currentToken.equals(pool.token1);
      if (isToken0 || isToken1) {
        // Direct match - swap through pool
        var nextPoolToken = isToken0 ? pool.token1 : pool.token0;
        tokenPath.push(nextPoolToken);
        steps.push({
          type: BoostedRouteStepType.SWAP,
          tokenIn: currentToken,
          tokenOut: nextPoolToken,
          pool: pool
        });
        currentToken = nextPoolToken;
      } else {
        // No direct match - need wrap/unwrap step before using pool
        var tokenForPool = null;
        if (!currentToken.isBoosted) {
          // Current is underlying, check if pool has boosted version
          var boostedInPool = [pool.token0, pool.token1].find(function (t) {
            return t.isBoosted && 'underlying' in t && t.underlying.equals(currentToken);
          });
          if (boostedInPool) {
            // Wrap: underlying → boosted
            tokenPath.push(boostedInPool);
            steps.push({
              type: BoostedRouteStepType.WRAP,
              tokenIn: currentToken,
              tokenOut: boostedInPool
            });
            tokenForPool = boostedInPool;
          }
        } else if ('underlying' in currentToken && currentToken.underlying) {
          // Current is boosted, check if pool has underlying version
          var underlying = currentToken.underlying;
          var underlyingInPool = [pool.token0, pool.token1].find(function (t) {
            return t.equals(underlying);
          });
          if (underlyingInPool) {
            // Unwrap: boosted → underlying
            tokenPath.push(underlyingInPool);
            steps.push({
              type: BoostedRouteStepType.UNWRAP,
              tokenIn: currentToken,
              tokenOut: underlyingInPool
            });
            tokenForPool = underlyingInPool;
          }
        }
        if (!tokenForPool) {
          throw new Error("Cannot connect " + currentToken.symbol + " to pool " + i);
        }
        // Now swap through pool using the wrapped/unwrapped token
        var _nextPoolToken = tokenForPool.equals(pool.token0) ? pool.token1 : pool.token0;
        tokenPath.push(_nextPoolToken);
        steps.push({
          type: BoostedRouteStepType.SWAP,
          tokenIn: tokenForPool,
          tokenOut: _nextPoolToken,
          pool: pool
        });
        currentToken = _nextPoolToken;
      }
    };
    for (var i = 0; i < pools.length; i++) {
      _loop();
    }
    // Check if we need to unwrap final output
    var lastToken = tokenPath[tokenPath.length - 1];
    if (lastToken.isBoosted && 'underlying' in lastToken && lastToken.underlying && !wrappedOutput.isBoosted && lastToken.underlying.equals(wrappedOutput)) {
      tokenPath.push(lastToken.underlying);
      steps.push({
        type: BoostedRouteStepType.UNWRAP,
        tokenIn: lastToken,
        tokenOut: lastToken.underlying
      });
    } else if (!lastToken.isBoosted && wrappedOutput.isBoosted && 'underlying' in wrappedOutput && wrappedOutput.underlying && wrappedOutput.underlying.equals(lastToken)) {
      // Need to wrap final token to match output
      tokenPath.push(wrappedOutput);
      steps.push({
        type: BoostedRouteStepType.WRAP,
        tokenIn: lastToken,
        tokenOut: wrappedOutput
      });
    }
    this.pools = pools;
    this.tokenPath = tokenPath;
    this.steps = steps;
    this.input = input;
    this.output = output;
  }
  /**
   * Returns the mid price of the route
   *
   * NOTE: For BoostedRoute this returns a 1:1 stub price.
   * The real midPrice calculation requires async exchange rate fetching
   *
   */
  _createClass(BoostedRoute, [{
    key: "midPrice",
    get: function get() {
      if (this._midPrice !== null) return this._midPrice;
      return this._midPrice = new Price(this.input, this.output, 1, 1);
    }
  }, {
    key: "chainId",
    get: function get() {
      if (this.pools.length === 0) {
        // For direct wrap/unwrap, get chainId from input or output
        return this.input.chainId;
      }
      return this.pools[0].chainId;
    }
  }]);
  return BoostedRoute;
}();

var MIN_NATIVE_CURRENCY_FOR_GAS = /*#__PURE__*/JSBI.exponentiate( /*#__PURE__*/JSBI.BigInt(10), /*#__PURE__*/JSBI.BigInt(16)); // .01 ETH
/**
 * Given some token amount, return the max that can be spent of it
 * @param currencyAmount to return max of
 */
function maxAmountSpend(currencyAmount) {
  if (!currencyAmount) return undefined;
  if (currencyAmount.currency.isNative) {
    if (JSBI.greaterThan(currencyAmount.quotient, MIN_NATIVE_CURRENCY_FOR_GAS)) {
      return CurrencyAmount.fromRawAmount(currencyAmount.currency, JSBI.subtract(currencyAmount.quotient, MIN_NATIVE_CURRENCY_FOR_GAS));
    } else {
      return CurrencyAmount.fromRawAmount(currencyAmount.currency, JSBI.BigInt(0));
    }
  }
  return currencyAmount;
}

var parseBalance = function parseBalance(value, decimals) {
  if (decimals === void 0) {
    decimals = 18;
  }
  return parseUnits(value || '0', decimals);
};
// try to parse a user entered amount for a given token
function tryParseAmount(value, currency) {
  if (!value || !currency) {
    return undefined;
  }
  try {
    var typedValueParsed = parseUnits(value, currency == null ? void 0 : currency.decimals).toString();
    if (typedValueParsed !== '0') {
      return CurrencyAmount.fromRawAmount(currency, JSBI.BigInt(typedValueParsed));
    }
  } catch (error) {
    // should fail if the user specifies too many decimal places of precision (or maybe exceed max uint?)
    console.debug("Failed to parse input amount: \"" + value + "\"", error);
  }
  // necessary for all paths to return a value
  return undefined;
}

function wait(ms) {
  return new Promise(function (resolve) {
    return setTimeout(resolve, ms);
  });
}
function waitRandom(min, max) {
  return wait(min + Math.round(Math.random() * Math.max(0, max - min)));
}
/**
 * This error is thrown if the function is cancelled before completing
 */
var CancelledError = /*#__PURE__*/function (_Error) {
  _inheritsLoose(CancelledError, _Error);
  function CancelledError() {
    var _this;
    _this = _Error.call(this, 'Cancelled') || this;
    _this.isCancelledError = true;
    return _this;
  }
  return CancelledError;
}( /*#__PURE__*/_wrapNativeSuper(Error));
/**
 * Throw this error if the function should retry
 */
var RetryableError = /*#__PURE__*/function (_Error2) {
  _inheritsLoose(RetryableError, _Error2);
  function RetryableError() {
    var _this2;
    _this2 = _Error2.apply(this, arguments) || this;
    _this2.isRetryableError = true;
    return _this2;
  }
  return RetryableError;
}( /*#__PURE__*/_wrapNativeSuper(Error));
/**
 * Retries the function that returns the promise until the promise successfully resolves up to n retries
 * @param fn function to retry
 * @param n how many times to retry
 * @param minWait min wait between retries in ms
 * @param maxWait max wait between retries in ms
 */
function retry(fn, _ref) {
  var n = _ref.n,
    minWait = _ref.minWait,
    maxWait = _ref.maxWait;
  var completed = false;
  var rejectCancelled;
  var promise = new Promise( /*#__PURE__*/function () {
    var _ref2 = _asyncToGenerator( /*#__PURE__*/_regeneratorRuntime().mark(function _callee(resolve, reject) {
      var result, error;
      return _regeneratorRuntime().wrap(function _callee$(_context) {
        while (1) switch (_context.prev = _context.next) {
          case 0:
            rejectCancelled = reject;
          case 1:
            result = void 0;
            _context.prev = 3;
            _context.next = 6;
            return fn();
          case 6:
            result = _context.sent;
            if (!completed) {
              resolve(result);
              completed = true;
            }
            return _context.abrupt("break", 25);
          case 11:
            _context.prev = 11;
            _context.t0 = _context["catch"](3);
            if (!completed) {
              _context.next = 15;
              break;
            }
            return _context.abrupt("break", 25);
          case 15:
            error = _context.t0;
            if (!(n <= 0 || !error.isRetryableError)) {
              _context.next = 20;
              break;
            }
            reject(error);
            completed = true;
            return _context.abrupt("break", 25);
          case 20:
            n--;
          case 21:
            _context.next = 23;
            return waitRandom(minWait, maxWait);
          case 23:
            _context.next = 1;
            break;
          case 25:
          case "end":
            return _context.stop();
        }
      }, _callee, null, [[3, 11]]);
    }));
    return function (_x, _x2) {
      return _ref2.apply(this, arguments);
    };
  }());
  return {
    promise: promise,
    cancel: function cancel() {
      if (completed) return;
      completed = true;
      rejectCancelled(new CancelledError());
    }
  };
}

function tryParsePrice(baseToken, quoteToken, value) {
  var _fraction$length;
  if (!baseToken || !quoteToken || !value) {
    return undefined;
  }
  if (!value.match(/^\d*\.?\d+$/)) {
    return undefined;
  }
  var _value$split = value.split('.'),
    whole = _value$split[0],
    fraction = _value$split[1];
  var decimals = (_fraction$length = fraction == null ? void 0 : fraction.length) != null ? _fraction$length : 0;
  var withoutDecimals = JSBI.BigInt((whole != null ? whole : '') + (fraction != null ? fraction : ''));
  return new Price(baseToken, quoteToken, JSBI.multiply(JSBI.BigInt(Math.pow(10, decimals)), JSBI.BigInt(Math.pow(10, baseToken.decimals))), JSBI.multiply(withoutDecimals, JSBI.BigInt(Math.pow(10, quoteToken.decimals))));
}
function tryParseTick(baseToken, quoteToken, value, tickSpacing) {
  if (!baseToken || !quoteToken || !value || !tickSpacing) {
    return undefined;
  }
  var price = tryParsePrice(baseToken, quoteToken, value);
  if (!price) {
    return undefined;
  }
  var tick;
  // check price is within min/max bounds, if outside return min/max
  var sqrtRatioX96 = encodeSqrtRatioX96(price.numerator, price.denominator);
  if (JSBI.greaterThanOrEqual(sqrtRatioX96, TickMath.MAX_SQRT_RATIO)) {
    tick = TickMath.MAX_TICK;
  } else if (JSBI.lessThanOrEqual(sqrtRatioX96, TickMath.MIN_SQRT_RATIO)) {
    tick = TickMath.MIN_TICK;
  } else {
    // this function is agnostic to the base, will always return the correct tick
    tick = priceToClosestTick(price);
  }
  return nearestUsableTick(tick, tickSpacing);
}

function unwrappedToken(currency) {
  var _currency$symbol, _currency$name;
  if (currency.isNative) return currency;
  if (currency.equals(WNATIVE[currency.chainId])) return Native.onChain(currency.chainId, (_currency$symbol = currency.symbol) != null ? _currency$symbol : '', (_currency$name = currency.name) != null ? _currency$name : '');
  return currency;
}

var algebraPositionManagerABI = [{
  "inputs": [{
    "internalType": "address",
    "name": "_factory",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "_WNativeToken",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "_tokenDescriptor_",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "_poolDeployer",
    "type": "address"
  }],
  "stateMutability": "nonpayable",
  "type": "constructor"
}, {
  "inputs": [],
  "name": "tickOutOfRange",
  "type": "error"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "address",
    "name": "owner",
    "type": "address"
  }, {
    "indexed": true,
    "internalType": "address",
    "name": "approved",
    "type": "address"
  }, {
    "indexed": true,
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "Approval",
  "type": "event"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "address",
    "name": "owner",
    "type": "address"
  }, {
    "indexed": true,
    "internalType": "address",
    "name": "operator",
    "type": "address"
  }, {
    "indexed": false,
    "internalType": "bool",
    "name": "approved",
    "type": "bool"
  }],
  "name": "ApprovalForAll",
  "type": "event"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }, {
    "indexed": false,
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }],
  "name": "Collect",
  "type": "event"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "uint128",
    "name": "liquidity",
    "type": "uint128"
  }, {
    "indexed": false,
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }],
  "name": "DecreaseLiquidity",
  "type": "event"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "FarmingFailed",
  "type": "event"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "uint128",
    "name": "liquidityDesired",
    "type": "uint128"
  }, {
    "indexed": false,
    "internalType": "uint128",
    "name": "actualLiquidity",
    "type": "uint128"
  }, {
    "indexed": false,
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }, {
    "indexed": false,
    "internalType": "address",
    "name": "pool",
    "type": "address"
  }],
  "name": "IncreaseLiquidity",
  "type": "event"
}, {
  "anonymous": false,
  "inputs": [{
    "indexed": true,
    "internalType": "address",
    "name": "from",
    "type": "address"
  }, {
    "indexed": true,
    "internalType": "address",
    "name": "to",
    "type": "address"
  }, {
    "indexed": true,
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "Transfer",
  "type": "event"
}, {
  "inputs": [],
  "name": "DOMAIN_SEPARATOR",
  "outputs": [{
    "internalType": "bytes32",
    "name": "",
    "type": "bytes32"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "NONFUNGIBLE_POSITION_MANAGER_ADMINISTRATOR_ROLE",
  "outputs": [{
    "internalType": "bytes32",
    "name": "",
    "type": "bytes32"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "PERMIT_TYPEHASH",
  "outputs": [{
    "internalType": "bytes32",
    "name": "",
    "type": "bytes32"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "WNativeToken",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "amount0Owed",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "amount1Owed",
    "type": "uint256"
  }, {
    "internalType": "bytes",
    "name": "data",
    "type": "bytes"
  }],
  "name": "algebraMintCallback",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "to",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "approve",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "internalType": "bool",
    "name": "approve",
    "type": "bool"
  }, {
    "internalType": "address",
    "name": "farmingAddress",
    "type": "address"
  }],
  "name": "approveForFarming",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "owner",
    "type": "address"
  }],
  "name": "balanceOf",
  "outputs": [{
    "internalType": "uint256",
    "name": "",
    "type": "uint256"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "burn",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "uint256",
      "name": "tokenId",
      "type": "uint256"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint128",
      "name": "amount0Max",
      "type": "uint128"
    }, {
      "internalType": "uint128",
      "name": "amount1Max",
      "type": "uint128"
    }],
    "internalType": "struct INonfungiblePositionManager.CollectParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "collect",
  "outputs": [{
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token0",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "token1",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "deployer",
    "type": "address"
  }, {
    "internalType": "uint160",
    "name": "sqrtPriceX96",
    "type": "uint160"
  }, {
    "internalType": "bytes",
    "name": "data",
    "type": "bytes"
  }],
  "name": "createAndInitializePoolIfNecessary",
  "outputs": [{
    "internalType": "address",
    "name": "pool",
    "type": "address"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "uint256",
      "name": "tokenId",
      "type": "uint256"
    }, {
      "internalType": "uint128",
      "name": "liquidity",
      "type": "uint128"
    }, {
      "internalType": "uint256",
      "name": "amount0Min",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount1Min",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }],
    "internalType": "struct INonfungiblePositionManager.DecreaseLiquidityParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "decreaseLiquidity",
  "outputs": [{
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [],
  "name": "factory",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "farmingApprovals",
  "outputs": [{
    "internalType": "address",
    "name": "farmingCenterAddress",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "farmingCenter",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "getApproved",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "uint256",
      "name": "tokenId",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount0Desired",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount1Desired",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount0Min",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount1Min",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }],
    "internalType": "struct INonfungiblePositionManager.IncreaseLiquidityParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "increaseLiquidity",
  "outputs": [{
    "internalType": "uint128",
    "name": "liquidity",
    "type": "uint128"
  }, {
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "owner",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "operator",
    "type": "address"
  }],
  "name": "isApprovedForAll",
  "outputs": [{
    "internalType": "bool",
    "name": "",
    "type": "bool"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "spender",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "isApprovedOrOwner",
  "outputs": [{
    "internalType": "bool",
    "name": "",
    "type": "bool"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "address",
      "name": "token0",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "token1",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "deployer",
      "type": "address"
    }, {
      "internalType": "int24",
      "name": "tickLower",
      "type": "int24"
    }, {
      "internalType": "int24",
      "name": "tickUpper",
      "type": "int24"
    }, {
      "internalType": "uint256",
      "name": "amount0Desired",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount1Desired",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount0Min",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amount1Min",
      "type": "uint256"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }],
    "internalType": "struct INonfungiblePositionManager.MintParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "mint",
  "outputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "internalType": "uint128",
    "name": "liquidity",
    "type": "uint128"
  }, {
    "internalType": "uint256",
    "name": "amount0",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "amount1",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "bytes[]",
    "name": "data",
    "type": "bytes[]"
  }],
  "name": "multicall",
  "outputs": [{
    "internalType": "bytes[]",
    "name": "results",
    "type": "bytes[]"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [],
  "name": "name",
  "outputs": [{
    "internalType": "string",
    "name": "",
    "type": "string"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "ownerOf",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "spender",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "permit",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [],
  "name": "poolDeployer",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "positions",
  "outputs": [{
    "internalType": "uint88",
    "name": "nonce",
    "type": "uint88"
  }, {
    "internalType": "address",
    "name": "operator",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "token0",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "token1",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "deployer",
    "type": "address"
  }, {
    "internalType": "int24",
    "name": "tickLower",
    "type": "int24"
  }, {
    "internalType": "int24",
    "name": "tickUpper",
    "type": "int24"
  }, {
    "internalType": "uint128",
    "name": "liquidity",
    "type": "uint128"
  }, {
    "internalType": "uint256",
    "name": "feeGrowthInside0LastX128",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "feeGrowthInside1LastX128",
    "type": "uint256"
  }, {
    "internalType": "uint128",
    "name": "tokensOwed0",
    "type": "uint128"
  }, {
    "internalType": "uint128",
    "name": "tokensOwed1",
    "type": "uint128"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "refundNativeToken",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "from",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "to",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "safeTransferFrom",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "from",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "to",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "internalType": "bytes",
    "name": "data",
    "type": "bytes"
  }],
  "name": "safeTransferFrom",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "value",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermit",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "nonce",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "expiry",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitAllowed",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "nonce",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "expiry",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitAllowedIfNecessary",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "value",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitIfNecessary",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "operator",
    "type": "address"
  }, {
    "internalType": "bool",
    "name": "approved",
    "type": "bool"
  }],
  "name": "setApprovalForAll",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "newFarmingCenter",
    "type": "address"
  }],
  "name": "setFarmingCenter",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "bytes4",
    "name": "interfaceId",
    "type": "bytes4"
  }],
  "name": "supportsInterface",
  "outputs": [{
    "internalType": "bool",
    "name": "",
    "type": "bool"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "amountMinimum",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }],
  "name": "sweepToken",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }, {
    "internalType": "bool",
    "name": "toActive",
    "type": "bool"
  }],
  "name": "switchFarmingStatus",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [],
  "name": "symbol",
  "outputs": [{
    "internalType": "string",
    "name": "",
    "type": "string"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "index",
    "type": "uint256"
  }],
  "name": "tokenByIndex",
  "outputs": [{
    "internalType": "uint256",
    "name": "",
    "type": "uint256"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "tokenFarmedIn",
  "outputs": [{
    "internalType": "address",
    "name": "farmingCenterAddress",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "owner",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "index",
    "type": "uint256"
  }],
  "name": "tokenOfOwnerByIndex",
  "outputs": [{
    "internalType": "uint256",
    "name": "",
    "type": "uint256"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "tokenURI",
  "outputs": [{
    "internalType": "string",
    "name": "",
    "type": "string"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "totalSupply",
  "outputs": [{
    "internalType": "uint256",
    "name": "",
    "type": "uint256"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "from",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "to",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "tokenId",
    "type": "uint256"
  }],
  "name": "transferFrom",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "amountMinimum",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }],
  "name": "unwrapWNativeToken",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "stateMutability": "payable",
  "type": "receive"
}];

var algebraSwapRouterABI = [{
  "inputs": [{
    "internalType": "address",
    "name": "_factory",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "_WNativeToken",
    "type": "address"
  }, {
    "internalType": "address",
    "name": "_poolDeployer",
    "type": "address"
  }],
  "stateMutability": "nonpayable",
  "type": "constructor"
}, {
  "inputs": [],
  "name": "WNativeToken",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "int256",
    "name": "amount0Delta",
    "type": "int256"
  }, {
    "internalType": "int256",
    "name": "amount1Delta",
    "type": "int256"
  }, {
    "internalType": "bytes",
    "name": "_data",
    "type": "bytes"
  }],
  "name": "algebraSwapCallback",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "bytes",
      "name": "path",
      "type": "bytes"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountIn",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountOutMinimum",
      "type": "uint256"
    }],
    "internalType": "struct ISwapRouter.ExactInputParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "exactInput",
  "outputs": [{
    "internalType": "uint256",
    "name": "amountOut",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "address",
      "name": "tokenIn",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "tokenOut",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "deployer",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountIn",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountOutMinimum",
      "type": "uint256"
    }, {
      "internalType": "uint160",
      "name": "limitSqrtPrice",
      "type": "uint160"
    }],
    "internalType": "struct ISwapRouter.ExactInputSingleParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "exactInputSingle",
  "outputs": [{
    "internalType": "uint256",
    "name": "amountOut",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "address",
      "name": "tokenIn",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "tokenOut",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "deployer",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountIn",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountOutMinimum",
      "type": "uint256"
    }, {
      "internalType": "uint160",
      "name": "limitSqrtPrice",
      "type": "uint160"
    }],
    "internalType": "struct ISwapRouter.ExactInputSingleParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "exactInputSingleSupportingFeeOnTransferTokens",
  "outputs": [{
    "internalType": "uint256",
    "name": "amountOut",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "bytes",
      "name": "path",
      "type": "bytes"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountOut",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountInMaximum",
      "type": "uint256"
    }],
    "internalType": "struct ISwapRouter.ExactOutputParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "exactOutput",
  "outputs": [{
    "internalType": "uint256",
    "name": "amountIn",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "components": [{
      "internalType": "address",
      "name": "tokenIn",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "tokenOut",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "deployer",
      "type": "address"
    }, {
      "internalType": "address",
      "name": "recipient",
      "type": "address"
    }, {
      "internalType": "uint256",
      "name": "deadline",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountOut",
      "type": "uint256"
    }, {
      "internalType": "uint256",
      "name": "amountInMaximum",
      "type": "uint256"
    }, {
      "internalType": "uint160",
      "name": "limitSqrtPrice",
      "type": "uint160"
    }],
    "internalType": "struct ISwapRouter.ExactOutputSingleParams",
    "name": "params",
    "type": "tuple"
  }],
  "name": "exactOutputSingle",
  "outputs": [{
    "internalType": "uint256",
    "name": "amountIn",
    "type": "uint256"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [],
  "name": "factory",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "bytes[]",
    "name": "data",
    "type": "bytes[]"
  }],
  "name": "multicall",
  "outputs": [{
    "internalType": "bytes[]",
    "name": "results",
    "type": "bytes[]"
  }],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [],
  "name": "poolDeployer",
  "outputs": [{
    "internalType": "address",
    "name": "",
    "type": "address"
  }],
  "stateMutability": "view",
  "type": "function"
}, {
  "inputs": [],
  "name": "refundNativeToken",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "value",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermit",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "nonce",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "expiry",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitAllowed",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "nonce",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "expiry",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitAllowedIfNecessary",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "value",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitIfNecessary",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "amountMinimum",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }],
  "name": "sweepToken",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "amountMinimum",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "feeBips",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "feeRecipient",
    "type": "address"
  }],
  "name": "sweepTokenWithFee",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "amountMinimum",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }],
  "name": "unwrapWNativeToken",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "uint256",
    "name": "amountMinimum",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "recipient",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "feeBips",
    "type": "uint256"
  }, {
    "internalType": "address",
    "name": "feeRecipient",
    "type": "address"
  }],
  "name": "unwrapWNativeTokenWithFee",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "stateMutability": "payable",
  "type": "receive"
}];

var selfPermitABI = [{
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "value",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermit",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "nonce",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "expiry",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitAllowed",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "nonce",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "expiry",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitAllowedIfNecessary",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}, {
  "inputs": [{
    "internalType": "address",
    "name": "token",
    "type": "address"
  }, {
    "internalType": "uint256",
    "name": "value",
    "type": "uint256"
  }, {
    "internalType": "uint256",
    "name": "deadline",
    "type": "uint256"
  }, {
    "internalType": "uint8",
    "name": "v",
    "type": "uint8"
  }, {
    "internalType": "bytes32",
    "name": "r",
    "type": "bytes32"
  }, {
    "internalType": "bytes32",
    "name": "s",
    "type": "bytes32"
  }],
  "name": "selfPermitIfNecessary",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}];

var Bound;
(function (Bound) {
  Bound["LOWER"] = "LOWER";
  Bound["UPPER"] = "UPPER";
})(Bound || (Bound = {}));

var Field;
(function (Field) {
  Field["CURRENCY_A"] = "CURRENCY_A";
  Field["CURRENCY_B"] = "CURRENCY_B";
})(Field || (Field = {}));

function isAllowedPermit(permitOptions) {
  return 'nonce' in permitOptions;
}
var SelfPermit = /*#__PURE__*/function () {
  function SelfPermit() {}
  SelfPermit.encodePermit = function encodePermit(token, options) {
    return isAllowedPermit(options) ? SelfPermit.INTERFACE.encodeFunctionData('selfPermitAllowed', [token.address, toHex(options.nonce), toHex(options.expiry), options.v, options.r, options.s]) : SelfPermit.INTERFACE.encodeFunctionData('selfPermit', [token.address, toHex(options.amount), toHex(options.deadline), options.v, options.r, options.s]);
  };
  return SelfPermit;
}();
SelfPermit.INTERFACE = /*#__PURE__*/new Interface(selfPermitABI);

var _excluded = ["expectedCurrencyOwed0", "expectedCurrencyOwed1"];
var MaxUint128 = /*#__PURE__*/toHex( /*#__PURE__*/JSBI.subtract( /*#__PURE__*/JSBI.exponentiate( /*#__PURE__*/JSBI.BigInt(2), /*#__PURE__*/JSBI.BigInt(128)), /*#__PURE__*/JSBI.BigInt(1)));
// type guard
function isMint(options) {
  return Object.keys(options).some(function (k) {
    return k === 'recipient';
  });
}
var NonfungiblePositionManager = /*#__PURE__*/function (_SelfPermit) {
  _inheritsLoose(NonfungiblePositionManager, _SelfPermit);
  /**
   * Cannot be constructed.
   */
  function NonfungiblePositionManager() {
    return _SelfPermit.call(this) || this;
  }
  NonfungiblePositionManager.createCallParameters = function createCallParameters(pool, deployer) {
    return {
      calldata: this.encodeCreate(pool, deployer || pool.deployer),
      value: toHex(0)
    };
  };
  NonfungiblePositionManager.addCallParameters = function addCallParameters(position, options) {
    !JSBI.greaterThan(position.liquidity, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ZERO_LIQUIDITY') : invariant(false) : void 0;
    var calldatas = [];
    // get amounts
    var _position$mintAmounts = position.mintAmounts,
      amount0Desired = _position$mintAmounts.amount0,
      amount1Desired = _position$mintAmounts.amount1;
    // adjust for
    var minimumAmounts = position.mintAmountsWithSlippage(options.slippageTolerance);
    var amount0Min = toHex(minimumAmounts.amount0);
    var amount1Min = toHex(minimumAmounts.amount1);
    var deadline = toHex(options.deadline);
    // create pool if needed
    if (isMint(options) && options.createPool) {
      calldatas.push(this.encodeCreate(position.pool, options.deployer || position.pool.deployer));
    }
    // permits if necessary
    if (options.token0Permit) {
      calldatas.push(NonfungiblePositionManager.encodePermit(position.pool.token0, options.token0Permit));
    }
    if (options.token1Permit) {
      calldatas.push(NonfungiblePositionManager.encodePermit(position.pool.token1, options.token1Permit));
    }
    // mint
    if (isMint(options)) {
      var recipient = validateAndParseAddress(options.recipient);
      calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('mint', [{
        token0: position.pool.token0.address,
        token1: position.pool.token1.address,
        deployer: position.pool.deployer,
        tickLower: position.tickLower,
        tickUpper: position.tickUpper,
        amount0Desired: toHex(amount0Desired),
        amount1Desired: toHex(amount1Desired),
        amount0Min: amount0Min,
        amount1Min: amount1Min,
        recipient: recipient,
        deadline: deadline
      }]));
    } else {
      // increase
      calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('increaseLiquidity', [{
        tokenId: toHex(options.tokenId),
        amount0Desired: toHex(amount0Desired),
        amount1Desired: toHex(amount1Desired),
        amount0Min: amount0Min,
        amount1Min: amount1Min,
        deadline: deadline
      }]));
    }
    var value = toHex(0);
    if (options.useNative) {
      var wrapped = options.useNative.wrapped;
      !(position.pool.token0.equals(wrapped) || position.pool.token1.equals(wrapped)) ? process.env.NODE_ENV !== "production" ? invariant(false, 'NO_WNative') : invariant(false) : void 0;
      var wrappedValue = position.pool.token0.equals(wrapped) ? amount0Desired : amount1Desired;
      // we only need to refund if we're actually sending ETH
      if (JSBI.greaterThan(wrappedValue, ZERO)) {
        calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('refundNativeToken'));
      }
      value = toHex(wrappedValue);
    }
    return {
      calldata: calldatas,
      value: value
    };
  };
  NonfungiblePositionManager.collectCallParameters = function collectCallParameters(options) {
    var calldatas = NonfungiblePositionManager.encodeCollect(options);
    return {
      calldata: calldatas,
      value: toHex(0)
    };
  }
  /**
   * Produces the calldata for completely or partially exiting a position
   * @param position The position to exit
   * @param options Additional information necessary for generating the calldata
   * @returns The call parameters
   */;
  NonfungiblePositionManager.removeCallParameters = function removeCallParameters(position, options) {
    var calldatas = [];
    var deadline = toHex(options.deadline);
    var tokenId = toHex(options.tokenId);
    // construct a partial position with a percentage of liquidity
    var partialPosition = new Position({
      pool: position.pool,
      liquidity: options.liquidityPercentage.multiply(position.liquidity).quotient,
      tickLower: position.tickLower,
      tickUpper: position.tickUpper
    });
    !JSBI.greaterThan(partialPosition.liquidity, ZERO) ? process.env.NODE_ENV !== "production" ? invariant(false, 'ZERO_LIQUIDITY') : invariant(false) : void 0;
    // slippage-adjusted underlying amounts
    var _partialPosition$burn = partialPosition.burnAmountsWithSlippage(options.slippageTolerance),
      amount0Min = _partialPosition$burn.amount0,
      amount1Min = _partialPosition$burn.amount1;
    if (options.permit) {
      calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('permit', [validateAndParseAddress(options.permit.spender), tokenId, toHex(options.permit.deadline), options.permit.v, options.permit.r, options.permit.s]));
    }
    // remove liquidity
    calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('decreaseLiquidity', [{
      tokenId: tokenId,
      liquidity: toHex(partialPosition.liquidity),
      amount0Min: toHex(amount0Min),
      amount1Min: toHex(amount1Min),
      deadline: deadline
    }]));
    var _options$collectOptio = options.collectOptions,
      expectedCurrencyOwed0 = _options$collectOptio.expectedCurrencyOwed0,
      expectedCurrencyOwed1 = _options$collectOptio.expectedCurrencyOwed1,
      rest = _objectWithoutPropertiesLoose(_options$collectOptio, _excluded);
    calldatas.push.apply(calldatas, NonfungiblePositionManager.encodeCollect(_extends({
      tokenId: options.tokenId,
      // add the underlying value to the expected currency already owed
      expectedCurrencyOwed0: expectedCurrencyOwed0.add(CurrencyAmount.fromRawAmount(expectedCurrencyOwed0.currency, amount0Min)),
      expectedCurrencyOwed1: expectedCurrencyOwed1.add(CurrencyAmount.fromRawAmount(expectedCurrencyOwed1.currency, amount1Min))
    }, rest)));
    if (options.liquidityPercentage.equalTo(ONE)) {
      if (options.burnToken) {
        calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('burn', [tokenId]));
      }
    } else {
      !(options.burnToken !== true) ? process.env.NODE_ENV !== "production" ? invariant(false, 'CANNOT_BURN') : invariant(false) : void 0;
    }
    return {
      calldata: calldatas,
      value: toHex(0)
    };
  };
  NonfungiblePositionManager.encodeCreate = function encodeCreate(pool, deployer) {
    return NonfungiblePositionManager.INTERFACE.encodeFunctionData('createAndInitializePoolIfNecessary', [pool.token0.address, pool.token1.address, deployer, toHex(pool.sqrtRatioX96), '0x']);
  };
  NonfungiblePositionManager.encodeCollect = function encodeCollect(options) {
    var calldatas = [];
    var tokenId = toHex(options.tokenId);
    var involvesETH = options.expectedCurrencyOwed0.currency.isNative || options.expectedCurrencyOwed1.currency.isNative;
    var recipient = validateAndParseAddress(options.recipient);
    // collect
    calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('collect', [{
      tokenId: tokenId,
      recipient: involvesETH ? ADDRESS_ZERO : recipient,
      amount0Max: MaxUint128,
      amount1Max: MaxUint128
    }]));
    if (involvesETH) {
      var ethAmount = options.expectedCurrencyOwed0.currency.isNative ? options.expectedCurrencyOwed0.quotient : options.expectedCurrencyOwed1.quotient;
      var token = options.expectedCurrencyOwed0.currency.isNative ? options.expectedCurrencyOwed1.currency : options.expectedCurrencyOwed0.currency;
      var tokenAmount = options.expectedCurrencyOwed0.currency.isNative ? options.expectedCurrencyOwed1.quotient : options.expectedCurrencyOwed0.quotient;
      calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('unwrapWNativeToken', [toHex(ethAmount), recipient]));
      calldatas.push(NonfungiblePositionManager.INTERFACE.encodeFunctionData('sweepToken', [token.address, toHex(tokenAmount), recipient]));
    }
    return calldatas;
  };
  return NonfungiblePositionManager;
}(SelfPermit);
NonfungiblePositionManager.INTERFACE = /*#__PURE__*/new Interface(algebraPositionManagerABI);

/**
 * Represents the SwapRouter, and has static methods for helping execute trades.
 */
var SwapRouter = /*#__PURE__*/function (_SelfPermit) {
  _inheritsLoose(SwapRouter, _SelfPermit);
  /**
   * Cannot be constructed.
   */
  function SwapRouter() {
    return _SelfPermit.call(this) || this;
  }
  /**
   * Produces the on-chain method name to call and the hex encoded parameters to pass as arguments for a given trade.
   * @param trade to produce call parameters for
   * @param options options for the call parameters
   */
  SwapRouter.swapCallParameters = function swapCallParameters(trades, options) {
    if (!Array.isArray(trades)) {
      trades = [trades];
    }
    var sampleTrade = trades[0];
    var tokenIn = sampleTrade.inputAmount.currency.wrapped;
    var tokenOut = sampleTrade.outputAmount.currency.wrapped;
    // All trades should have the same starting and ending token.
    !trades.every(function (trade) {
      return trade.inputAmount.currency.wrapped.equals(tokenIn);
    }) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN_IN_DIFF') : invariant(false) : void 0;
    !trades.every(function (trade) {
      return trade.outputAmount.currency.wrapped.equals(tokenOut);
    }) ? process.env.NODE_ENV !== "production" ? invariant(false, 'TOKEN_OUT_DIFF') : invariant(false) : void 0;
    var calldatas = [];
    var ZERO_IN = CurrencyAmount.fromRawAmount(trades[0].inputAmount.currency, 0);
    var ZERO_OUT = CurrencyAmount.fromRawAmount(trades[0].outputAmount.currency, 0);
    var totalAmountOut = trades.reduce(function (sum, trade) {
      return sum.add(trade.minimumAmountOut(options.slippageTolerance));
    }, ZERO_OUT);
    // flag for whether a refund needs to happen
    var mustRefund = sampleTrade.inputAmount.currency.isNative && sampleTrade.tradeType === TradeType.EXACT_OUTPUT;
    var inputIsNative = sampleTrade.inputAmount.currency.isNative;
    // flags for whether funds should be send first to the router
    var outputIsNative = sampleTrade.outputAmount.currency.isNative;
    var routerMustCustody = outputIsNative || !!options.fee;
    var totalValue = inputIsNative ? trades.reduce(function (sum, trade) {
      return sum.add(trade.maximumAmountIn(options.slippageTolerance));
    }, ZERO_IN) : ZERO_IN;
    // encode permit if necessary
    if (options.inputTokenPermit) {
      !sampleTrade.inputAmount.currency.isToken ? process.env.NODE_ENV !== "production" ? invariant(false, 'NON_TOKEN_PERMIT') : invariant(false) : void 0;
      calldatas.push(SwapRouter.encodePermit(sampleTrade.inputAmount.currency, options.inputTokenPermit));
    }
    var recipient = validateAndParseAddress(options.recipient);
    var deadline = toHex(options.deadline);
    for (var _iterator = _createForOfIteratorHelperLoose(trades), _step; !(_step = _iterator()).done;) {
      var trade = _step.value;
      for (var _iterator2 = _createForOfIteratorHelperLoose(trade.swaps), _step2; !(_step2 = _iterator2()).done;) {
        var _step2$value = _step2.value,
          route = _step2$value.route,
          inputAmount = _step2$value.inputAmount,
          outputAmount = _step2$value.outputAmount;
        var amountIn = toHex(trade.maximumAmountIn(options.slippageTolerance, inputAmount).quotient);
        var amountOut = toHex(trade.minimumAmountOut(options.slippageTolerance, outputAmount).quotient);
        // flag for whether the trade is single hop or not
        var singleHop = route.pools.length === 1;
        if (singleHop) {
          if (trade.tradeType === TradeType.EXACT_INPUT) {
            var _options$sqrtPriceLim;
            var exactInputSingleParams = {
              tokenIn: route.tokenPath[0].address,
              tokenOut: route.tokenPath[1].address,
              deployer: ADDRESS_ZERO,
              recipient: routerMustCustody ? ADDRESS_ZERO : recipient,
              deadline: deadline,
              amountIn: amountIn,
              amountOutMinimum: amountOut,
              limitSqrtPrice: toHex((_options$sqrtPriceLim = options.sqrtPriceLimitX96) != null ? _options$sqrtPriceLim : 0)
            };
            calldatas.push(SwapRouter.INTERFACE.encodeFunctionData(options.feeOnTransfer && !inputIsNative ? 'exactInputSingleSupportingFeeOnTransferTokens' : 'exactInputSingle', [exactInputSingleParams]));
          } else {
            var _options$sqrtPriceLim2;
            var exactOutputSingleParams = {
              tokenIn: route.tokenPath[0].address,
              tokenOut: route.tokenPath[1].address,
              recipient: routerMustCustody ? ADDRESS_ZERO : recipient,
              deployer: ADDRESS_ZERO,
              deadline: deadline,
              amountOut: amountOut,
              amountInMaximum: amountIn,
              limitSqrtPrice: toHex((_options$sqrtPriceLim2 = options.sqrtPriceLimitX96) != null ? _options$sqrtPriceLim2 : 0)
            };
            calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('exactOutputSingle', [exactOutputSingleParams]));
          }
        } else {
          !(options.sqrtPriceLimitX96 === undefined) ? process.env.NODE_ENV !== "production" ? invariant(false, 'MULTIHOP_PRICE_LIMIT') : invariant(false) : void 0;
          var path = encodeRouteToPath(route, trade.tradeType === TradeType.EXACT_OUTPUT);
          if (trade.tradeType === TradeType.EXACT_INPUT) {
            var exactInputParams = {
              path: path,
              recipient: routerMustCustody ? ADDRESS_ZERO : recipient,
              deadline: deadline,
              amountIn: amountIn,
              amountOutMinimum: amountOut
            };
            calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('exactInput', [exactInputParams]));
          } else {
            var exactOutputParams = {
              path: path,
              recipient: routerMustCustody ? ADDRESS_ZERO : recipient,
              deadline: deadline,
              amountOut: amountOut,
              amountInMaximum: amountIn
            };
            calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('exactOutput', [exactOutputParams]));
          }
        }
      }
    }
    // unwrap
    if (routerMustCustody) {
      if (!!options.fee) {
        var feeRecipient = validateAndParseAddress(options.fee.recipient);
        var fee = toHex(options.fee.fee.multiply(10000).quotient);
        if (outputIsNative) {
          calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('unwrapWNativeTokenWithFee', [toHex(totalAmountOut.quotient), recipient, fee, feeRecipient]));
        } else {
          calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('sweepTokenWithFee', [sampleTrade.outputAmount.currency.wrapped.address, toHex(totalAmountOut.quotient), recipient, fee, feeRecipient]));
        }
      } else {
        calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('unwrapWNativeToken', [toHex(totalAmountOut.quotient), recipient]));
      }
    }
    // refund
    if (mustRefund) {
      calldatas.push(SwapRouter.INTERFACE.encodeFunctionData('refundNativeToken'));
    }
    return {
      calldata: calldatas,
      value: toHex(totalValue.quotient)
    };
  };
  return SwapRouter;
}(SelfPermit);
SwapRouter.INTERFACE = /*#__PURE__*/new Interface(algebraSwapRouterABI);

export { ADDRESS_ZERO, BoostedRoute, BoostedRouteStepType, BoostedToken, Bound, ChainId, CurrencyAmount, DEFAULT_TICK_SPACING, ExtendedNative, Field, Fraction, FullMath, INITIAL_POOL_FEE, LiquidityMath, MaxUint128, MaxUint256, NEGATIVE_ONE, Native, NoTickDataProvider, NonfungiblePositionManager, ONE, POOL_DEPLOYER_ADDRESSES, POOL_INIT_CODE_HASH, Percent, Pool, Position, Price, Q192, Q96, RetryableError, Rounding, Route, SelfPermit, SqrtPriceMath, SwapRouter, Tick, TickList, TickListDataProvider, TickMath, Token, Trade, TradeType, WNATIVE, ZERO, algebraPositionManagerABI, algebraSwapRouterABI, computeCustomPoolAddress, computePoolAddress, computePoolAddressZkSync, currencyEquals, encodeRouteToPath, encodeSqrtRatioX96, getTickToPrice, isSorted, maxAmountSpend, maxLiquidityForAmounts, mostSignificantBit, nearestUsableTick, parseBalance, priceToClosestTick, retry, selfPermitABI, tickToPrice, toHex, tradeComparator, tryParseAmount, tryParsePrice, tryParseTick, unwrappedToken };
//# sourceMappingURL=integral-sdk.esm.js.map
