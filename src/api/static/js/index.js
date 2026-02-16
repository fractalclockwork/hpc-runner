(
  function () {
    const t = document.createElement('link').relList;
    if (t && t.supports && t.supports('modulepreload')) return;
    for (
      const l of document.querySelectorAll('link[rel="modulepreload"]')
    ) r(l);
    new MutationObserver(
      l => {
        for (const i of l) if (i.type === 'childList') for (const s of i.addedNodes) s.tagName === 'LINK' &&
        s.rel === 'modulepreload' &&
        r(s)
      }
    ).observe(document, {
      childList: !0,
      subtree: !0
    });
    function n(l) {
      const i = {};
      return l.integrity &&
      (i.integrity = l.integrity),
      l.referrerPolicy &&
      (i.referrerPolicy = l.referrerPolicy),
      l.crossOrigin === 'use-credentials' ? i.credentials = 'include' : l.crossOrigin === 'anonymous' ? i.credentials = 'omit' : i.credentials = 'same-origin',
      i
    }
    function r(l) {
      if (l.ep) return;
      l.ep = !0;
      const i = n(l);
      fetch(l.href, i)
    }
  }
) ();
var Xo = {
  exports: {
  }
},
nl = {},
Zo = {
  exports: {
  }
},
z = {}; /**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Zn = Symbol.for('react.element'),
pc = Symbol.for('react.portal'),
mc = Symbol.for('react.fragment'),
hc = Symbol.for('react.strict_mode'),
vc = Symbol.for('react.profiler'),
yc = Symbol.for('react.provider'),
gc = Symbol.for('react.context'),
xc = Symbol.for('react.forward_ref'),
wc = Symbol.for('react.suspense'),
kc = Symbol.for('react.memo'),
Sc = Symbol.for('react.lazy'),
Is = Symbol.iterator;
function Nc(e) {
  return e === null ||
  typeof e != 'object' ? null : (e = Is && e[Is] || e['@@iterator'], typeof e == 'function' ? e : null)
}
var Jo = {
  isMounted: function () {
    return !1
  },
  enqueueForceUpdate: function () {
  },
  enqueueReplaceState: function () {
  },
  enqueueSetState: function () {
  }
},
qo = Object.assign,
bo = {};
function sn(e, t, n) {
  this.props = e,
  this.context = t,
  this.refs = bo,
  this.updater = n ||
  Jo
}
sn.prototype.isReactComponent = {};
sn.prototype.setState = function (e, t) {
  if (typeof e != 'object' && typeof e != 'function' && e != null) throw Error(
    'setState(...): takes an object of state variables to update or a function which returns an object of state variables.'
  );
  this.updater.enqueueSetState(this, e, t, 'setState')
};
sn.prototype.forceUpdate = function (e) {
  this.updater.enqueueForceUpdate(this, e, 'forceUpdate')
};
function eu() {
}
eu.prototype = sn.prototype;
function $i(e, t, n) {
  this.props = e,
  this.context = t,
  this.refs = bo,
  this.updater = n ||
  Jo
}
var Hi = $i.prototype = new eu;
Hi.constructor = $i;
qo(Hi, sn.prototype);
Hi.isPureReactComponent = !0;
var Fs = Array.isArray,
tu = Object.prototype.hasOwnProperty,
Vi = {
  current: null
},
nu = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ru(e, t, n) {
  var r,
  l = {},
  i = null,
  s = null;
  if (t != null) for (r in t.ref !== void 0 && (s = t.ref), t.key !== void 0 && (i = '' + t.key), t) tu.call(t, r) &&
  !nu.hasOwnProperty(r) &&
  (l[r] = t[r]);
  var u = arguments.length - 2;
  if (u === 1) l.children = n;
   else if (1 < u) {
    for (var a = Array(u), d = 0; d < u; d++) a[d] = arguments[d + 2];
    l.children = a
  }
  if (e && e.defaultProps) for (r in u = e.defaultProps, u) l[r] === void 0 &&
  (l[r] = u[r]);
  return {
    $$typeof: Zn,
    type: e,
    key: i,
    ref: s,
    props: l,
    _owner: Vi.current
  }
}
function jc(e, t) {
  return {
    $$typeof: Zn,
    type: e.type,
    key: t,
    ref: e.ref,
    props: e.props,
    _owner: e._owner
  }
}
function Bi(e) {
  return typeof e == 'object' &&
  e !== null &&
  e.$$typeof === Zn
}
function Cc(e) {
  var t = {
    '=': '=0',
    ':': '=2'
  };
  return '$' + e.replace(/[=:]/g, function (n) {
    return t[n]
  })
}
var Us = /\/+/g;
function kl(e, t) {
  return typeof e == 'object' &&
  e !== null &&
  e.key != null ? Cc('' + e.key) : t.toString(36)
}
function wr(e, t, n, r, l) {
  var i = typeof e;
  (i === 'undefined' || i === 'boolean') &&
  (e = null);
  var s = !1;
  if (e === null) s = !0;
   else switch (i) {
    case 'string':
    case 'number':
      s = !0;
      break;
    case 'object':
      switch (e.$$typeof) {
        case Zn:
        case pc:
          s = !0
      }
  }
  if (s) return s = e,
  l = l(s),
  e = r === '' ? '.' + kl(s, 0) : r,
  Fs(l) ? (
    n = '',
    e != null &&
    (n = e.replace(Us, '$&/') + '/'),
    wr(l, t, n, '', function (d) {
      return d
    })
  ) : l != null &&
  (
    Bi(l) &&
    (
      l = jc(
        l,
        n + (!l.key || s && s.key === l.key ? '' : ('' + l.key).replace(Us, '$&/') + '/') + e
      )
    ),
    t.push(l)
  ),
  1;
  if (s = 0, r = r === '' ? '.' : r + ':', Fs(e)) for (var u = 0; u < e.length; u++) {
    i = e[u];
    var a = r + kl(i, u);
    s += wr(i, t, n, a, l)
  } else if (a = Nc(e), typeof a == 'function') for (e = a.call(e), u = 0; !(i = e.next()).done; ) i = i.value,
  a = r + kl(i, u++),
  s += wr(i, t, n, a, l);
   else if (i === 'object') throw t = String(e),
  Error(
    'Objects are not valid as a React child (found: ' + (
      t === '[object Object]' ? 'object with keys {' + Object.keys(e).join(', ') + '}' : t
    ) + '). If you meant to render a collection of children, use an array instead.'
  );
  return s
}
function rr(e, t, n) {
  if (e == null) return e;
  var r = [],
  l = 0;
  return wr(e, r, '', '', function (i) {
    return t.call(n, i, l++)
  }),
  r
}
function Ec(e) {
  if (e._status === - 1) {
    var t = e._result;
    t = t(),
    t.then(
      function (n) {
        (e._status === 0 || e._status === - 1) &&
        (e._status = 1, e._result = n)
      },
      function (n) {
        (e._status === 0 || e._status === - 1) &&
        (e._status = 2, e._result = n)
      }
    ),
    e._status === - 1 &&
    (e._status = 0, e._result = t)
  }
  if (e._status === 1) return e._result.default;
  throw e._result
}
var ue = {
  current: null
},
kr = {
  transition: null
},
Pc = {
  ReactCurrentDispatcher: ue,
  ReactCurrentBatchConfig: kr,
  ReactCurrentOwner: Vi
};
function lu() {
  throw Error('act(...) is not supported in production builds of React.')
}
z.Children = {
  map: rr,
  forEach: function (e, t, n) {
    rr(e, function () {
      t.apply(this, arguments)
    }, n)
  },
  count: function (e) {
    var t = 0;
    return rr(e, function () {
      t++
    }),
    t
  },
  toArray: function (e) {
    return rr(e, function (t) {
      return t
    }) ||
    []
  },
  only: function (e) {
    if (!Bi(e)) throw Error(
      'React.Children.only expected to receive a single React element child.'
    );
    return e
  }
};
z.Component = sn;
z.Fragment = mc;
z.Profiler = vc;
z.PureComponent = $i;
z.StrictMode = hc;
z.Suspense = wc;
z.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = Pc;
z.act = lu;
z.cloneElement = function (e, t, n) {
  if (e == null) throw Error(
    'React.cloneElement(...): The argument must be a React element, but you passed ' + e + '.'
  );
  var r = qo({
  }, e.props),
  l = e.key,
  i = e.ref,
  s = e._owner;
  if (t != null) {
    if (
      t.ref !== void 0 &&
      (i = t.ref, s = Vi.current),
      t.key !== void 0 &&
      (l = '' + t.key),
      e.type &&
      e.type.defaultProps
    ) var u = e.type.defaultProps;
    for (a in t) tu.call(t, a) &&
    !nu.hasOwnProperty(a) &&
    (r[a] = t[a] === void 0 && u !== void 0 ? u[a] : t[a])
  }
  var a = arguments.length - 2;
  if (a === 1) r.children = n;
   else if (1 < a) {
    u = Array(a);
    for (var d = 0; d < a; d++) u[d] = arguments[d + 2];
    r.children = u
  }
  return {
    $$typeof: Zn,
    type: e.type,
    key: l,
    ref: i,
    props: r,
    _owner: s
  }
};
z.createContext = function (e) {
  return e = {
    $$typeof: gc,
    _currentValue: e,
    _currentValue2: e,
    _threadCount: 0,
    Provider: null,
    Consumer: null,
    _defaultValue: null,
    _globalName: null
  },
  e.Provider = {
    $$typeof: yc,
    _context: e
  },
  e.Consumer = e
};
z.createElement = ru;
z.createFactory = function (e) {
  var t = ru.bind(null, e);
  return t.type = e,
  t
};
z.createRef = function () {
  return {
    current: null
  }
};
z.forwardRef = function (e) {
  return {
    $$typeof: xc,
    render: e
  }
};
z.isValidElement = Bi;
z.lazy = function (e) {
  return {
    $$typeof: Sc,
    _payload: {
      _status: - 1,
      _result: e
    },
    _init: Ec
  }
};
z.memo = function (e, t) {
  return {
    $$typeof: kc,
    type: e,
    compare: t === void 0 ? null : t
  }
};
z.startTransition = function (e) {
  var t = kr.transition;
  kr.transition = {};
  try {
    e()
  } finally {
    kr.transition = t
  }
};
z.unstable_act = lu;
z.useCallback = function (e, t) {
  return ue.current.useCallback(e, t)
};
z.useContext = function (e) {
  return ue.current.useContext(e)
};
z.useDebugValue = function () {
};
z.useDeferredValue = function (e) {
  return ue.current.useDeferredValue(e)
};
z.useEffect = function (e, t) {
  return ue.current.useEffect(e, t)
};
z.useId = function () {
  return ue.current.useId()
};
z.useImperativeHandle = function (e, t, n) {
  return ue.current.useImperativeHandle(e, t, n)
};
z.useInsertionEffect = function (e, t) {
  return ue.current.useInsertionEffect(e, t)
};
z.useLayoutEffect = function (e, t) {
  return ue.current.useLayoutEffect(e, t)
};
z.useMemo = function (e, t) {
  return ue.current.useMemo(e, t)
};
z.useReducer = function (e, t, n) {
  return ue.current.useReducer(e, t, n)
};
z.useRef = function (e) {
  return ue.current.useRef(e)
};
z.useState = function (e) {
  return ue.current.useState(e)
};
z.useSyncExternalStore = function (e, t, n) {
  return ue.current.useSyncExternalStore(e, t, n)
};
z.useTransition = function () {
  return ue.current.useTransition()
};
z.version = '18.3.1';
Zo.exports = z;
var Ue = Zo.exports; /**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var _c = Ue,
Rc = Symbol.for('react.element'),
zc = Symbol.for('react.fragment'),
Tc = Object.prototype.hasOwnProperty,
Lc = _c.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,
Mc = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function iu(e, t, n) {
  var r,
  l = {},
  i = null,
  s = null;
  n !== void 0 &&
  (i = '' + n),
  t.key !== void 0 &&
  (i = '' + t.key),
  t.ref !== void 0 &&
  (s = t.ref);
  for (r in t) Tc.call(t, r) &&
  !Mc.hasOwnProperty(r) &&
  (l[r] = t[r]);
  if (e && e.defaultProps) for (r in t = e.defaultProps, t) l[r] === void 0 &&
  (l[r] = t[r]);
  return {
    $$typeof: Rc,
    type: e,
    key: i,
    ref: s,
    props: l,
    _owner: Lc.current
  }
}
nl.Fragment = zc;
nl.jsx = iu;
nl.jsxs = iu;
Xo.exports = nl;
var o = Xo.exports,
su = {
  exports: {
  }
},
xe = {},
ou = {
  exports: {
  }
},
uu = {}; /**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
(
  function (e) {
    function t(j, _) {
      var R = j.length;
      j.push(_);
      e: for (; 0 < R; ) {
        var W = R - 1 >>> 1,
        X = j[W];
        if (0 < l(X, _)) j[W] = _,
        j[R] = X,
        R = W;
         else break e
      }
    }
    function n(j) {
      return j.length === 0 ? null : j[0]
    }
    function r(j) {
      if (j.length === 0) return null;
      var _ = j[0],
      R = j.pop();
      if (R !== _) {
        j[0] = R;
        e: for (var W = 0, X = j.length, tr = X >>> 1; W < tr; ) {
          var yt = 2 * (W + 1) - 1,
          wl = j[yt],
          gt = yt + 1,
          nr = j[gt];
          if (0 > l(wl, R)) gt < X &&
          0 > l(nr, wl) ? (j[W] = nr, j[gt] = R, W = gt) : (j[W] = wl, j[yt] = R, W = yt);
           else if (gt < X && 0 > l(nr, R)) j[W] = nr,
          j[gt] = R,
          W = gt;
           else break e
        }
      }
      return _
    }
    function l(j, _) {
      var R = j.sortIndex - _.sortIndex;
      return R !== 0 ? R : j.id - _.id
    }
    if (
      typeof performance == 'object' &&
      typeof performance.now == 'function'
    ) {
      var i = performance;
      e.unstable_now = function () {
        return i.now()
      }
    } else {
      var s = Date,
      u = s.now();
      e.unstable_now = function () {
        return s.now() - u
      }
    }
    var a = [],
    d = [],
    v = 1,
    h = null,
    m = 3,
    x = !1,
    w = !1,
    k = !1,
    F = typeof setTimeout == 'function' ? setTimeout : null,
    f = typeof clearTimeout == 'function' ? clearTimeout : null,
    c = typeof setImmediate < 'u' ? setImmediate : null;
    typeof navigator < 'u' &&
    navigator.scheduling !== void 0 &&
    navigator.scheduling.isInputPending !== void 0 &&
    navigator.scheduling.isInputPending.bind(navigator.scheduling);
    function p(j) {
      for (var _ = n(d); _ !== null; ) {
        if (_.callback === null) r(d);
         else if (_.startTime <= j) r(d),
        _.sortIndex = _.expirationTime,
        t(a, _);
         else break;
        _ = n(d)
      }
    }
    function y(j) {
      if (k = !1, p(j), !w) if (n(a) !== null) w = !0,
      gl(N);
       else {
        var _ = n(d);
        _ !== null &&
        xl(y, _.startTime - j)
      }
    }
    function N(j, _) {
      w = !1,
      k &&
      (k = !1, f(P), P = - 1),
      x = !0;
      var R = m;
      try {
        for (p(_), h = n(a); h !== null && (!(h.expirationTime > _) || j && !Pe()); ) {
          var W = h.callback;
          if (typeof W == 'function') {
            h.callback = null,
            m = h.priorityLevel;
            var X = W(h.expirationTime <= _);
            _ = e.unstable_now(),
            typeof X == 'function' ? h.callback = X : h === n(a) &&
            r(a),
            p(_)
          } else r(a);
          h = n(a)
        }
        if (h !== null) var tr = !0;
         else {
          var yt = n(d);
          yt !== null &&
          xl(y, yt.startTime - _),
          tr = !1
        }
        return tr
      } finally {
        h = null,
        m = R,
        x = !1
      }
    }
    var C = !1,
    E = null,
    P = - 1,
    B = 5,
    T = - 1;
    function Pe() {
      return !(e.unstable_now() - T < B)
    }
    function an() {
      if (E !== null) {
        var j = e.unstable_now();
        T = j;
        var _ = !0;
        try {
          _ = E(!0, j)
        } finally {
          _ ? cn() : (C = !1, E = null)
        }
      } else C = !1
    }
    var cn;
    if (typeof c == 'function') cn = function () {
      c(an)
    };
     else if (typeof MessageChannel < 'u') {
      var Ds = new MessageChannel,
      fc = Ds.port2;
      Ds.port1.onmessage = an,
      cn = function () {
        fc.postMessage(null)
      }
    } else cn = function () {
      F(an, 0)
    };
    function gl(j) {
      E = j,
      C ||
      (C = !0, cn())
    }
    function xl(j, _) {
      P = F(function () {
        j(e.unstable_now())
      }, _)
    }
    e.unstable_IdlePriority = 5,
    e.unstable_ImmediatePriority = 1,
    e.unstable_LowPriority = 4,
    e.unstable_NormalPriority = 3,
    e.unstable_Profiling = null,
    e.unstable_UserBlockingPriority = 2,
    e.unstable_cancelCallback = function (j) {
      j.callback = null
    },
    e.unstable_continueExecution = function () {
      w ||
      x ||
      (w = !0, gl(N))
    },
    e.unstable_forceFrameRate = function (j) {
      0 > j ||
      125 < j ? console.error(
        'forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported'
      ) : B = 0 < j ? Math.floor(1000 / j) : 5
    },
    e.unstable_getCurrentPriorityLevel = function () {
      return m
    },
    e.unstable_getFirstCallbackNode = function () {
      return n(a)
    },
    e.unstable_next = function (j) {
      switch (m) {
        case 1:
        case 2:
        case 3:
          var _ = 3;
          break;
        default:
          _ = m
      }
      var R = m;
      m = _;
      try {
        return j()
      } finally {
        m = R
      }
    },
    e.unstable_pauseExecution = function () {
    },
    e.unstable_requestPaint = function () {
    },
    e.unstable_runWithPriority = function (j, _) {
      switch (j) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
          break;
        default:
          j = 3
      }
      var R = m;
      m = j;
      try {
        return _()
      } finally {
        m = R
      }
    },
    e.unstable_scheduleCallback = function (j, _, R) {
      var W = e.unstable_now();
      switch (
          typeof R == 'object' &&
          R !== null ? (R = R.delay, R = typeof R == 'number' && 0 < R ? W + R : W) : R = W,
          j
        ) {
        case 1:
          var X = - 1;
          break;
        case 2:
          X = 250;
          break;
        case 5:
          X = 1073741823;
          break;
        case 4:
          X = 10000;
          break;
        default:
          X = 5000
      }
      return X = R + X,
      j = {
        id: v++,
        callback: _,
        priorityLevel: j,
        startTime: R,
        expirationTime: X,
        sortIndex: - 1
      },
      R > W ? (
        j.sortIndex = R,
        t(d, j),
        n(a) === null &&
        j === n(d) &&
        (k ? (f(P), P = - 1) : k = !0, xl(y, R - W))
      ) : (j.sortIndex = X, t(a, j), w || x || (w = !0, gl(N))),
      j
    },
    e.unstable_shouldYield = Pe,
    e.unstable_wrapCallback = function (j) {
      var _ = m;
      return function () {
        var R = m;
        m = _;
        try {
          return j.apply(this, arguments)
        } finally {
          m = R
        }
      }
    }
  }
) (uu);
ou.exports = uu;
var Oc = ou.exports; /**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Dc = Ue,
ge = Oc;
function g(e) {
  for (
    var t = 'https://reactjs.org/docs/error-decoder.html?invariant=' + e,
    n = 1;
    n < arguments.length;
    n++
  ) t += '&args[]=' + encodeURIComponent(arguments[n]);
  return 'Minified React error #' + e + '; visit ' + t + ' for the full message or use the non-minified dev environment for full errors and additional helpful warnings.'
}
var au = new Set,
Mn = {};
function Tt(e, t) {
  qt(e, t),
  qt(e + 'Capture', t)
}
function qt(e, t) {
  for (Mn[e] = t, e = 0; e < t.length; e++) au.add(t[e])
}
var Ke = !(
  typeof window > 'u' ||
  typeof window.document > 'u' ||
  typeof window.document.createElement > 'u'
),
Gl = Object.prototype.hasOwnProperty,
Ic = /^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,
As = {},
$s = {};
function Fc(e) {
  return Gl.call($s, e) ? !0 : Gl.call(As, e) ? !1 : Ic.test(e) ? $s[e] = !0 : (As[e] = !0, !1)
}
function Uc(e, t, n, r) {
  if (n !== null && n.type === 0) return !1;
  switch (typeof t) {
    case 'function':
    case 'symbol':
      return !0;
    case 'boolean':
      return r ? !1 : n !== null ? !n.acceptsBooleans : (e = e.toLowerCase().slice(0, 5), e !== 'data-' && e !== 'aria-');
    default:
      return !1
  }
}
function Ac(e, t, n, r) {
  if (t === null || typeof t > 'u' || Uc(e, t, n, r)) return !0;
  if (r) return !1;
  if (n !== null) switch (n.type) {
    case 3:
      return !t;
    case 4:
      return t === !1;
    case 5:
      return isNaN(t);
    case 6:
      return isNaN(t) ||
      1 > t
  }
  return !1
}
function ae(e, t, n, r, l, i, s) {
  this.acceptsBooleans = t === 2 ||
  t === 3 ||
  t === 4,
  this.attributeName = r,
  this.attributeNamespace = l,
  this.mustUseProperty = n,
  this.propertyName = e,
  this.type = t,
  this.sanitizeURL = i,
  this.removeEmptyString = s
}
var ee = {};
'children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style'.split(' ').forEach(function (e) {
  ee[e] = new ae(e, 0, !1, e, null, !1, !1)
});
[
  ['acceptCharset',
  'accept-charset'],
  [
    'className',
    'class'
  ],
  [
    'htmlFor',
    'for'
  ],
  [
    'httpEquiv',
    'http-equiv'
  ]
].forEach(function (e) {
  var t = e[0];
  ee[t] = new ae(t, 1, !1, e[1], null, !1, !1)
});
[
  'contentEditable',
  'draggable',
  'spellCheck',
  'value'
].forEach(function (e) {
  ee[e] = new ae(e, 2, !1, e.toLowerCase(), null, !1, !1)
});
[
  'autoReverse',
  'externalResourcesRequired',
  'focusable',
  'preserveAlpha'
].forEach(function (e) {
  ee[e] = new ae(e, 2, !1, e, null, !1, !1)
});
'allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope'.split(' ').forEach(function (e) {
  ee[e] = new ae(e, 3, !1, e.toLowerCase(), null, !1, !1)
});
[
  'checked',
  'multiple',
  'muted',
  'selected'
].forEach(function (e) {
  ee[e] = new ae(e, 3, !0, e, null, !1, !1)
});
[
  'capture',
  'download'
].forEach(function (e) {
  ee[e] = new ae(e, 4, !1, e, null, !1, !1)
});
[
  'cols',
  'rows',
  'size',
  'span'
].forEach(function (e) {
  ee[e] = new ae(e, 6, !1, e, null, !1, !1)
});
[
  'rowSpan',
  'start'
].forEach(function (e) {
  ee[e] = new ae(e, 5, !1, e.toLowerCase(), null, !1, !1)
});
var Wi = /[\-:]([a-z])/g;
function Qi(e) {
  return e[1].toUpperCase()
}
'accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height'.split(' ').forEach(
  function (e) {
    var t = e.replace(Wi, Qi);
    ee[t] = new ae(t, 1, !1, e, null, !1, !1)
  }
);
'xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type'.split(' ').forEach(
  function (e) {
    var t = e.replace(Wi, Qi);
    ee[t] = new ae(t, 1, !1, e, 'http://www.w3.org/1999/xlink', !1, !1)
  }
);
[
  'xml:base',
  'xml:lang',
  'xml:space'
].forEach(
  function (e) {
    var t = e.replace(Wi, Qi);
    ee[t] = new ae(t, 1, !1, e, 'http://www.w3.org/XML/1998/namespace', !1, !1)
  }
);
[
  'tabIndex',
  'crossOrigin'
].forEach(function (e) {
  ee[e] = new ae(e, 1, !1, e.toLowerCase(), null, !1, !1)
});
ee.xlinkHref = new ae(
  'xlinkHref',
  1,
  !1,
  'xlink:href',
  'http://www.w3.org/1999/xlink',
  !0,
  !1
);
[
  'src',
  'href',
  'action',
  'formAction'
].forEach(function (e) {
  ee[e] = new ae(e, 1, !1, e.toLowerCase(), null, !0, !0)
});
function Ki(e, t, n, r) {
  var l = ee.hasOwnProperty(t) ? ee[t] : null;
  (
    l !== null ? l.type !== 0 : r ||
    !(2 < t.length) ||
    t[0] !== 'o' &&
    t[0] !== 'O' ||
    t[1] !== 'n' &&
    t[1] !== 'N'
  ) &&
  (
    Ac(t, n, l, r) &&
    (n = null),
    r ||
    l === null ? Fc(t) &&
    (n === null ? e.removeAttribute(t) : e.setAttribute(t, '' + n)) : l.mustUseProperty ? e[l.propertyName] = n === null ? l.type === 3 ? !1 : '' : n : (
      t = l.attributeName,
      r = l.attributeNamespace,
      n === null ? e.removeAttribute(t) : (
        l = l.type,
        n = l === 3 ||
        l === 4 &&
        n === !0 ? '' : '' + n,
        r ? e.setAttributeNS(r, t, n) : e.setAttribute(t, n)
      )
    )
  )
}
var Ze = Dc.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,
lr = Symbol.for('react.element'),
Ot = Symbol.for('react.portal'),
Dt = Symbol.for('react.fragment'),
Gi = Symbol.for('react.strict_mode'),
Yl = Symbol.for('react.profiler'),
cu = Symbol.for('react.provider'),
du = Symbol.for('react.context'),
Yi = Symbol.for('react.forward_ref'),
Xl = Symbol.for('react.suspense'),
Zl = Symbol.for('react.suspense_list'),
Xi = Symbol.for('react.memo'),
qe = Symbol.for('react.lazy'),
fu = Symbol.for('react.offscreen'),
Hs = Symbol.iterator;
function dn(e) {
  return e === null ||
  typeof e != 'object' ? null : (e = Hs && e[Hs] || e['@@iterator'], typeof e == 'function' ? e : null)
}
var H = Object.assign,
Sl;
function xn(e) {
  if (Sl === void 0) try {
    throw Error()
  } catch (n) {
    var t = n.stack.trim().match(/\n( *(at )?)/);
    Sl = t &&
    t[1] ||
    ''
  }
  return `

  ` + Sl + e
}
var Nl = !1;
function jl(e, t) {
  if (!e || Nl) return '';
  Nl = !0;
  var n = Error.prepareStackTrace;
  Error.prepareStackTrace = void 0;
  try {
    if (t) if (
      t = function () {
        throw Error()
      },
      Object.defineProperty(t.prototype, 'props', {
        set: function () {
          throw Error()
        }
      }),
      typeof Reflect == 'object' &&
      Reflect.construct
    ) {
      try {
        Reflect.construct(t, [])
      } catch (d) {
        var r = d
      }
      Reflect.construct(e, [], t)
    } else {
      try {
        t.call()
      } catch (d) {
        r = d
      }
      e.call(t.prototype)
    } else {
      try {
        throw Error()
      } catch (d) {
        r = d
      }
      e()
    }
  } catch (d) {
    if (d && r && typeof d.stack == 'string') {
      for (
        var l = d.stack.split(`

        `),
        i = r.stack.split(`

        `),
        s = l.length - 1,
        u = i.length - 1;
        1 <= s &&
        0 <= u &&
        l[s] !== i[u];
      ) u--;
      for (; 1 <= s && 0 <= u; s--, u--) if (l[s] !== i[u]) {
        if (s !== 1 || u !== 1) do if (s--, u--, 0 > u || l[s] !== i[u]) {
          var a = `

          ` + l[s].replace(' at new ', ' at ');
          return e.displayName &&
          a.includes('<anonymous>') &&
          (a = a.replace('<anonymous>', e.displayName)),
          a
        } while (1 <= s && 0 <= u);
        break
      }
    }
  } finally {
    Nl = !1,
    Error.prepareStackTrace = n
  }
  return (e = e ? e.displayName ||
  e.name : '') ? xn(e) : ''
}
function $c(e) {
  switch (e.tag) {
    case 5:
      return xn(e.type);
    case 16:
      return xn('Lazy');
    case 13:
      return xn('Suspense');
    case 19:
      return xn('SuspenseList');
    case 0:
    case 2:
    case 15:
      return e = jl(e.type, !1),
      e;
    case 11:
      return e = jl(e.type.render, !1),
      e;
    case 1:
      return e = jl(e.type, !0),
      e;
    default:
      return ''
  }
}
function Jl(e) {
  if (e == null) return null;
  if (typeof e == 'function') return e.displayName ||
  e.name ||
  null;
  if (typeof e == 'string') return e;
  switch (e) {
    case Dt:
      return 'Fragment';
    case Ot:
      return 'Portal';
    case Yl:
      return 'Profiler';
    case Gi:
      return 'StrictMode';
    case Xl:
      return 'Suspense';
    case Zl:
      return 'SuspenseList'
  }
  if (typeof e == 'object') switch (e.$$typeof) {
    case du:
      return (e.displayName || 'Context') + '.Consumer';
    case cu:
      return (e._context.displayName || 'Context') + '.Provider';
    case Yi:
      var t = e.render;
      return e = e.displayName,
      e ||
      (
        e = t.displayName ||
        t.name ||
        '',
        e = e !== '' ? 'ForwardRef(' + e + ')' : 'ForwardRef'
      ),
      e;
    case Xi:
      return t = e.displayName ||
      null,
      t !== null ? t : Jl(e.type) ||
      'Memo';
    case qe:
      t = e._payload,
      e = e._init;
      try {
        return Jl(e(t))
      } catch {
      }
  }
  return null
}
function Hc(e) {
  var t = e.type;
  switch (e.tag) {
    case 24:
      return 'Cache';
    case 9:
      return (t.displayName || 'Context') + '.Consumer';
    case 10:
      return (t._context.displayName || 'Context') + '.Provider';
    case 18:
      return 'DehydratedFragment';
    case 11:
      return e = t.render,
      e = e.displayName ||
      e.name ||
      '',
      t.displayName ||
      (e !== '' ? 'ForwardRef(' + e + ')' : 'ForwardRef');
    case 7:
      return 'Fragment';
    case 5:
      return t;
    case 4:
      return 'Portal';
    case 3:
      return 'Root';
    case 6:
      return 'Text';
    case 16:
      return Jl(t);
    case 8:
      return t === Gi ? 'StrictMode' : 'Mode';
    case 22:
      return 'Offscreen';
    case 12:
      return 'Profiler';
    case 21:
      return 'Scope';
    case 13:
      return 'Suspense';
    case 19:
      return 'SuspenseList';
    case 25:
      return 'TracingMarker';
    case 1:
    case 0:
    case 17:
    case 2:
    case 14:
    case 15:
      if (typeof t == 'function') return t.displayName ||
      t.name ||
      null;
      if (typeof t == 'string') return t
  }
  return null
}
function ft(e) {
  switch (typeof e) {
    case 'boolean':
    case 'number':
    case 'string':
    case 'undefined':
      return e;
    case 'object':
      return e;
    default:
      return ''
  }
}
function pu(e) {
  var t = e.type;
  return (e = e.nodeName) &&
  e.toLowerCase() === 'input' &&
  (t === 'checkbox' || t === 'radio')
}
function Vc(e) {
  var t = pu(e) ? 'checked' : 'value',
  n = Object.getOwnPropertyDescriptor(e.constructor.prototype, t),
  r = '' + e[t];
  if (
    !e.hasOwnProperty(t) &&
    typeof n < 'u' &&
    typeof n.get == 'function' &&
    typeof n.set == 'function'
  ) {
    var l = n.get,
    i = n.set;
    return Object.defineProperty(
      e,
      t,
      {
        configurable: !0,
        get: function () {
          return l.call(this)
        },
        set: function (s) {
          r = '' + s,
          i.call(this, s)
        }
      }
    ),
    Object.defineProperty(e, t, {
      enumerable: n.enumerable
    }),
    {
      getValue: function () {
        return r
      },
      setValue: function (s) {
        r = '' + s
      },
      stopTracking: function () {
        e._valueTracker = null,
        delete e[t]
      }
    }
  }
}
function ir(e) {
  e._valueTracker ||
  (e._valueTracker = Vc(e))
}
function mu(e) {
  if (!e) return !1;
  var t = e._valueTracker;
  if (!t) return !0;
  var n = t.getValue(),
  r = '';
  return e &&
  (r = pu(e) ? e.checked ? 'true' : 'false' : e.value),
  e = r,
  e !== n ? (t.setValue(e), !0) : !1
}
function Lr(e) {
  if (e = e || (typeof document < 'u' ? document : void 0), typeof e > 'u') return null;
  try {
    return e.activeElement ||
    e.body
  } catch {
    return e.body
  }
}
function ql(e, t) {
  var n = t.checked;
  return H({
  }, t, {
    defaultChecked: void 0,
    defaultValue: void 0,
    value: void 0,
    checked: n ?? e._wrapperState.initialChecked
  })
}
function Vs(e, t) {
  var n = t.defaultValue == null ? '' : t.defaultValue,
  r = t.checked != null ? t.checked : t.defaultChecked;
  n = ft(t.value != null ? t.value : n),
  e._wrapperState = {
    initialChecked: r,
    initialValue: n,
    controlled: t.type === 'checkbox' ||
    t.type === 'radio' ? t.checked != null : t.value != null
  }
}
function hu(e, t) {
  t = t.checked,
  t != null &&
  Ki(e, 'checked', t, !1)
}
function bl(e, t) {
  hu(e, t);
  var n = ft(t.value),
  r = t.type;
  if (n != null) r === 'number' ? (n === 0 && e.value === '' || e.value != n) &&
  (e.value = '' + n) : e.value !== '' + n &&
  (e.value = '' + n);
   else if (r === 'submit' || r === 'reset') {
    e.removeAttribute('value');
    return
  }
  t.hasOwnProperty('value') ? ei(e, t.type, n) : t.hasOwnProperty('defaultValue') &&
  ei(e, t.type, ft(t.defaultValue)),
  t.checked == null &&
  t.defaultChecked != null &&
  (e.defaultChecked = !!t.defaultChecked)
}
function Bs(e, t, n) {
  if (t.hasOwnProperty('value') || t.hasOwnProperty('defaultValue')) {
    var r = t.type;
    if (
      !(r !== 'submit' && r !== 'reset' || t.value !== void 0 && t.value !== null)
    ) return;
    t = '' + e._wrapperState.initialValue,
    n ||
    t === e.value ||
    (e.value = t),
    e.defaultValue = t
  }
  n = e.name,
  n !== '' &&
  (e.name = ''),
  e.defaultChecked = !!e._wrapperState.initialChecked,
  n !== '' &&
  (e.name = n)
}
function ei(e, t, n) {
  (t !== 'number' || Lr(e.ownerDocument) !== e) &&
  (
    n == null ? e.defaultValue = '' + e._wrapperState.initialValue : e.defaultValue !== '' + n &&
    (e.defaultValue = '' + n)
  )
}
var wn = Array.isArray;
function Kt(e, t, n, r) {
  if (e = e.options, t) {
    t = {};
    for (var l = 0; l < n.length; l++) t['$' + n[l]] = !0;
    for (n = 0; n < e.length; n++) l = t.hasOwnProperty('$' + e[n].value),
    e[n].selected !== l &&
    (e[n].selected = l),
    l &&
    r &&
    (e[n].defaultSelected = !0)
  } else {
    for (n = '' + ft(n), t = null, l = 0; l < e.length; l++) {
      if (e[l].value === n) {
        e[l].selected = !0,
        r &&
        (e[l].defaultSelected = !0);
        return
      }
      t !== null ||
      e[l].disabled ||
      (t = e[l])
    }
    t !== null &&
    (t.selected = !0)
  }
}
function ti(e, t) {
  if (t.dangerouslySetInnerHTML != null) throw Error(g(91));
  return H({
  }, t, {
    value: void 0,
    defaultValue: void 0,
    children: '' + e._wrapperState.initialValue
  })
}
function Ws(e, t) {
  var n = t.value;
  if (n == null) {
    if (n = t.children, t = t.defaultValue, n != null) {
      if (t != null) throw Error(g(92));
      if (wn(n)) {
        if (1 < n.length) throw Error(g(93));
        n = n[0]
      }
      t = n
    }
    t == null &&
    (t = ''),
    n = t
  }
  e._wrapperState = {
    initialValue: ft(n)
  }
}
function vu(e, t) {
  var n = ft(t.value),
  r = ft(t.defaultValue);
  n != null &&
  (
    n = '' + n,
    n !== e.value &&
    (e.value = n),
    t.defaultValue == null &&
    e.defaultValue !== n &&
    (e.defaultValue = n)
  ),
  r != null &&
  (e.defaultValue = '' + r)
}
function Qs(e) {
  var t = e.textContent;
  t === e._wrapperState.initialValue &&
  t !== '' &&
  t !== null &&
  (e.value = t)
}
function yu(e) {
  switch (e) {
    case 'svg':
      return 'http://www.w3.org/2000/svg';
    case 'math':
      return 'http://www.w3.org/1998/Math/MathML';
    default:
      return 'http://www.w3.org/1999/xhtml'
  }
}
function ni(e, t) {
  return e == null ||
  e === 'http://www.w3.org/1999/xhtml' ? yu(t) : e === 'http://www.w3.org/2000/svg' &&
  t === 'foreignObject' ? 'http://www.w3.org/1999/xhtml' : e
}
var sr,
gu = function (e) {
  return typeof MSApp < 'u' &&
  MSApp.execUnsafeLocalFunction ? function (t, n, r, l) {
    MSApp.execUnsafeLocalFunction(function () {
      return e(t, n, r, l)
    })
  }
   : e
}(
  function (e, t) {
    if (
      e.namespaceURI !== 'http://www.w3.org/2000/svg' ||
      'innerHTML' in e
    ) e.innerHTML = t;
     else {
      for (
        sr = sr ||
        document.createElement('div'),
        sr.innerHTML = '<svg>' + t.valueOf().toString() + '</svg>',
        t = sr.firstChild;
        e.firstChild;
      ) e.removeChild(e.firstChild);
      for (; t.firstChild; ) e.appendChild(t.firstChild)
    }
  }
);
function On(e, t) {
  if (t) {
    var n = e.firstChild;
    if (n && n === e.lastChild && n.nodeType === 3) {
      n.nodeValue = t;
      return
    }
  }
  e.textContent = t
}
var jn = {
  animationIterationCount: !0,
  aspectRatio: !0,
  borderImageOutset: !0,
  borderImageSlice: !0,
  borderImageWidth: !0,
  boxFlex: !0,
  boxFlexGroup: !0,
  boxOrdinalGroup: !0,
  columnCount: !0,
  columns: !0,
  flex: !0,
  flexGrow: !0,
  flexPositive: !0,
  flexShrink: !0,
  flexNegative: !0,
  flexOrder: !0,
  gridArea: !0,
  gridRow: !0,
  gridRowEnd: !0,
  gridRowSpan: !0,
  gridRowStart: !0,
  gridColumn: !0,
  gridColumnEnd: !0,
  gridColumnSpan: !0,
  gridColumnStart: !0,
  fontWeight: !0,
  lineClamp: !0,
  lineHeight: !0,
  opacity: !0,
  order: !0,
  orphans: !0,
  tabSize: !0,
  widows: !0,
  zIndex: !0,
  zoom: !0,
  fillOpacity: !0,
  floodOpacity: !0,
  stopOpacity: !0,
  strokeDasharray: !0,
  strokeDashoffset: !0,
  strokeMiterlimit: !0,
  strokeOpacity: !0,
  strokeWidth: !0
},
Bc = [
  'Webkit',
  'ms',
  'Moz',
  'O'
];
Object.keys(jn).forEach(
  function (e) {
    Bc.forEach(
      function (t) {
        t = t + e.charAt(0).toUpperCase() + e.substring(1),
        jn[t] = jn[e]
      }
    )
  }
);
function xu(e, t, n) {
  return t == null ||
  typeof t == 'boolean' ||
  t === '' ? '' : n ||
  typeof t != 'number' ||
  t === 0 ||
  jn.hasOwnProperty(e) &&
  jn[e] ? ('' + t).trim() : t + 'px'
}
function wu(e, t) {
  e = e.style;
  for (var n in t) if (t.hasOwnProperty(n)) {
    var r = n.indexOf('--') === 0,
    l = xu(n, t[n], r);
    n === 'float' &&
    (n = 'cssFloat'),
    r ? e.setProperty(n, l) : e[n] = l
  }
}
var Wc = H({
  menuitem: !0
}, {
  area: !0,
  base: !0,
  br: !0,
  col: !0,
  embed: !0,
  hr: !0,
  img: !0,
  input: !0,
  keygen: !0,
  link: !0,
  meta: !0,
  param: !0,
  source: !0,
  track: !0,
  wbr: !0
});
function ri(e, t) {
  if (t) {
    if (Wc[e] && (t.children != null || t.dangerouslySetInnerHTML != null)) throw Error(g(137, e));
    if (t.dangerouslySetInnerHTML != null) {
      if (t.children != null) throw Error(g(60));
      if (
        typeof t.dangerouslySetInnerHTML != 'object' ||
        !('__html' in t.dangerouslySetInnerHTML)
      ) throw Error(g(61))
    }
    if (t.style != null && typeof t.style != 'object') throw Error(g(62))
  }
}
function li(e, t) {
  if (e.indexOf('-') === - 1) return typeof t.is == 'string';
  switch (e) {
    case 'annotation-xml':
    case 'color-profile':
    case 'font-face':
    case 'font-face-src':
    case 'font-face-uri':
    case 'font-face-format':
    case 'font-face-name':
    case 'missing-glyph':
      return !1;
    default:
      return !0
  }
}
var ii = null;
function Zi(e) {
  return e = e.target ||
  e.srcElement ||
  window,
  e.correspondingUseElement &&
  (e = e.correspondingUseElement),
  e.nodeType === 3 ? e.parentNode : e
}
var si = null,
Gt = null,
Yt = null;
function Ks(e) {
  if (e = bn(e)) {
    if (typeof si != 'function') throw Error(g(280));
    var t = e.stateNode;
    t &&
    (t = ol(t), si(e.stateNode, e.type, t))
  }
}
function ku(e) {
  Gt ? Yt ? Yt.push(e) : Yt = [
    e
  ] : Gt = e
}
function Su() {
  if (Gt) {
    var e = Gt,
    t = Yt;
    if (Yt = Gt = null, Ks(e), t) for (e = 0; e < t.length; e++) Ks(t[e])
  }
}
function Nu(e, t) {
  return e(t)
}
function ju() {
}
var Cl = !1;
function Cu(e, t, n) {
  if (Cl) return e(t, n);
  Cl = !0;
  try {
    return Nu(e, t, n)
  } finally {
    Cl = !1,
    (Gt !== null || Yt !== null) &&
    (ju(), Su())
  }
}
function Dn(e, t) {
  var n = e.stateNode;
  if (n === null) return null;
  var r = ol(n);
  if (r === null) return null;
  n = r[t];
  e: switch (t) {
    case 'onClick':
    case 'onClickCapture':
    case 'onDoubleClick':
    case 'onDoubleClickCapture':
    case 'onMouseDown':
    case 'onMouseDownCapture':
    case 'onMouseMove':
    case 'onMouseMoveCapture':
    case 'onMouseUp':
    case 'onMouseUpCapture':
    case 'onMouseEnter':
      (r = !r.disabled) ||
      (
        e = e.type,
        r = !(e === 'button' || e === 'input' || e === 'select' || e === 'textarea')
      ),
      e = !r;
      break e;
    default:
      e = !1
  }
  if (e) return null;
  if (n && typeof n != 'function') throw Error(g(231, t, typeof n));
  return n
}
var oi = !1;
if (Ke) try {
  var fn = {};
  Object.defineProperty(fn, 'passive', {
    get: function () {
      oi = !0
    }
  }),
  window.addEventListener('test', fn, fn),
  window.removeEventListener('test', fn, fn)
} catch {
  oi = !1
}
function Qc(e, t, n, r, l, i, s, u, a) {
  var d = Array.prototype.slice.call(arguments, 3);
  try {
    t.apply(n, d)
  } catch (v) {
    this.onError(v)
  }
}
var Cn = !1,
Mr = null,
Or = !1,
ui = null,
Kc = {
  onError: function (e) {
    Cn = !0,
    Mr = e
  }
};
function Gc(e, t, n, r, l, i, s, u, a) {
  Cn = !1,
  Mr = null,
  Qc.apply(Kc, arguments)
}
function Yc(e, t, n, r, l, i, s, u, a) {
  if (Gc.apply(this, arguments), Cn) {
    if (Cn) {
      var d = Mr;
      Cn = !1,
      Mr = null
    } else throw Error(g(198));
    Or ||
    (Or = !0, ui = d)
  }
}
function Lt(e) {
  var t = e,
  n = e;
  if (e.alternate) for (; t.return; ) t = t.return;
   else {
    e = t;
    do t = e,
    t.flags & 4098 &&
    (n = t.return),
    e = t.return;
    while (e)
  }
  return t.tag === 3 ? n : null
}
function Eu(e) {
  if (e.tag === 13) {
    var t = e.memoizedState;
    if (
      t === null &&
      (e = e.alternate, e !== null && (t = e.memoizedState)),
      t !== null
    ) return t.dehydrated
  }
  return null
}
function Gs(e) {
  if (Lt(e) !== e) throw Error(g(188))
}
function Xc(e) {
  var t = e.alternate;
  if (!t) {
    if (t = Lt(e), t === null) throw Error(g(188));
    return t !== e ? null : e
  }
  for (var n = e, r = t; ; ) {
    var l = n.return;
    if (l === null) break;
    var i = l.alternate;
    if (i === null) {
      if (r = l.return, r !== null) {
        n = r;
        continue
      }
      break
    }
    if (l.child === i.child) {
      for (i = l.child; i; ) {
        if (i === n) return Gs(l),
        e;
        if (i === r) return Gs(l),
        t;
        i = i.sibling
      }
      throw Error(g(188))
    }
    if (n.return !== r.return) n = l,
    r = i;
     else {
      for (var s = !1, u = l.child; u; ) {
        if (u === n) {
          s = !0,
          n = l,
          r = i;
          break
        }
        if (u === r) {
          s = !0,
          r = l,
          n = i;
          break
        }
        u = u.sibling
      }
      if (!s) {
        for (u = i.child; u; ) {
          if (u === n) {
            s = !0,
            n = i,
            r = l;
            break
          }
          if (u === r) {
            s = !0,
            r = i,
            n = l;
            break
          }
          u = u.sibling
        }
        if (!s) throw Error(g(189))
      }
    }
    if (n.alternate !== r) throw Error(g(190))
  }
  if (n.tag !== 3) throw Error(g(188));
  return n.stateNode.current === n ? e : t
}
function Pu(e) {
  return e = Xc(e),
  e !== null ? _u(e) : null
}
function _u(e) {
  if (e.tag === 5 || e.tag === 6) return e;
  for (e = e.child; e !== null; ) {
    var t = _u(e);
    if (t !== null) return t;
    e = e.sibling
  }
  return null
}
var Ru = ge.unstable_scheduleCallback,
Ys = ge.unstable_cancelCallback,
Zc = ge.unstable_shouldYield,
Jc = ge.unstable_requestPaint,
Q = ge.unstable_now,
qc = ge.unstable_getCurrentPriorityLevel,
Ji = ge.unstable_ImmediatePriority,
zu = ge.unstable_UserBlockingPriority,
Dr = ge.unstable_NormalPriority,
bc = ge.unstable_LowPriority,
Tu = ge.unstable_IdlePriority,
rl = null,
Ae = null;
function ed(e) {
  if (Ae && typeof Ae.onCommitFiberRoot == 'function') try {
    Ae.onCommitFiberRoot(rl, e, void 0, (e.current.flags & 128) === 128)
  } catch {
  }
}
var Le = Math.clz32 ? Math.clz32 : rd,
td = Math.log,
nd = Math.LN2;
function rd(e) {
  return e >>>= 0,
  e === 0 ? 32 : 31 - (td(e) / nd | 0) | 0
}
var or = 64,
ur = 4194304;
function kn(e) {
  switch (e & - e) {
    case 1:
      return 1;
    case 2:
      return 2;
    case 4:
      return 4;
    case 8:
      return 8;
    case 16:
      return 16;
    case 32:
      return 32;
    case 64:
    case 128:
    case 256:
    case 512:
    case 1024:
    case 2048:
    case 4096:
    case 8192:
    case 16384:
    case 32768:
    case 65536:
    case 131072:
    case 262144:
    case 524288:
    case 1048576:
    case 2097152:
      return e & 4194240;
    case 4194304:
    case 8388608:
    case 16777216:
    case 33554432:
    case 67108864:
      return e & 130023424;
    case 134217728:
      return 134217728;
    case 268435456:
      return 268435456;
    case 536870912:
      return 536870912;
    case 1073741824:
      return 1073741824;
    default:
      return e
  }
}
function Ir(e, t) {
  var n = e.pendingLanes;
  if (n === 0) return 0;
  var r = 0,
  l = e.suspendedLanes,
  i = e.pingedLanes,
  s = n & 268435455;
  if (s !== 0) {
    var u = s & ~l;
    u !== 0 ? r = kn(u) : (i &= s, i !== 0 && (r = kn(i)))
  } else s = n & ~l,
  s !== 0 ? r = kn(s) : i !== 0 &&
  (r = kn(i));
  if (r === 0) return 0;
  if (
    t !== 0 &&
    t !== r &&
    !(t & l) &&
    (l = r & - r, i = t & - t, l >= i || l === 16 && (i & 4194240) !== 0)
  ) return t;
  if (r & 4 && (r |= n & 16), t = e.entangledLanes, t !== 0) for (e = e.entanglements, t &= r; 0 < t; ) n = 31 - Le(t),
  l = 1 << n,
  r |= e[n],
  t &= ~l;
  return r
}
function ld(e, t) {
  switch (e) {
    case 1:
    case 2:
    case 4:
      return t + 250;
    case 8:
    case 16:
    case 32:
    case 64:
    case 128:
    case 256:
    case 512:
    case 1024:
    case 2048:
    case 4096:
    case 8192:
    case 16384:
    case 32768:
    case 65536:
    case 131072:
    case 262144:
    case 524288:
    case 1048576:
    case 2097152:
      return t + 5000;
    case 4194304:
    case 8388608:
    case 16777216:
    case 33554432:
    case 67108864:
      return - 1;
    case 134217728:
    case 268435456:
    case 536870912:
    case 1073741824:
      return - 1;
    default:
      return - 1
  }
}
function id(e, t) {
  for (
    var n = e.suspendedLanes,
    r = e.pingedLanes,
    l = e.expirationTimes,
    i = e.pendingLanes;
    0 < i;
  ) {
    var s = 31 - Le(i),
    u = 1 << s,
    a = l[s];
    a === - 1 ? (!(u & n) || u & r) &&
    (l[s] = ld(u, t)) : a <= t &&
    (e.expiredLanes |= u),
    i &= ~u
  }
}
function ai(e) {
  return e = e.pendingLanes & - 1073741825,
  e !== 0 ? e : e & 1073741824 ? 1073741824 : 0
}
function Lu() {
  var e = or;
  return or <<= 1,
  !(or & 4194240) &&
  (or = 64),
  e
}
function El(e) {
  for (var t = [], n = 0; 31 > n; n++) t.push(e);
  return t
}
function Jn(e, t, n) {
  e.pendingLanes |= t,
  t !== 536870912 &&
  (e.suspendedLanes = 0, e.pingedLanes = 0),
  e = e.eventTimes,
  t = 31 - Le(t),
  e[t] = n
}
function sd(e, t) {
  var n = e.pendingLanes & ~t;
  e.pendingLanes = t,
  e.suspendedLanes = 0,
  e.pingedLanes = 0,
  e.expiredLanes &= t,
  e.mutableReadLanes &= t,
  e.entangledLanes &= t,
  t = e.entanglements;
  var r = e.eventTimes;
  for (e = e.expirationTimes; 0 < n; ) {
    var l = 31 - Le(n),
    i = 1 << l;
    t[l] = 0,
    r[l] = - 1,
    e[l] = - 1,
    n &= ~i
  }
}
function qi(e, t) {
  var n = e.entangledLanes |= t;
  for (e = e.entanglements; n; ) {
    var r = 31 - Le(n),
    l = 1 << r;
    l & t | e[r] & t &&
    (e[r] |= t),
    n &= ~l
  }
}
var M = 0;
function Mu(e) {
  return e &= - e,
  1 < e ? 4 < e ? e & 268435455 ? 16 : 536870912 : 4 : 1
}
var Ou,
bi,
Du,
Iu,
Fu,
ci = !1,
ar = [],
lt = null,
it = null,
st = null,
In = new Map,
Fn = new Map,
et = [],
od = 'mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit'.split(' ');
function Xs(e, t) {
  switch (e) {
    case 'focusin':
    case 'focusout':
      lt = null;
      break;
    case 'dragenter':
    case 'dragleave':
      it = null;
      break;
    case 'mouseover':
    case 'mouseout':
      st = null;
      break;
    case 'pointerover':
    case 'pointerout':
      In.delete(t.pointerId);
      break;
    case 'gotpointercapture':
    case 'lostpointercapture':
      Fn.delete(t.pointerId)
  }
}
function pn(e, t, n, r, l, i) {
  return e === null ||
  e.nativeEvent !== i ? (
    e = {
      blockedOn: t,
      domEventName: n,
      eventSystemFlags: r,
      nativeEvent: i,
      targetContainers: [
        l
      ]
    },
    t !== null &&
    (t = bn(t), t !== null && bi(t)),
    e
  ) : (
    e.eventSystemFlags |= r,
    t = e.targetContainers,
    l !== null &&
    t.indexOf(l) === - 1 &&
    t.push(l),
    e
  )
}
function ud(e, t, n, r, l) {
  switch (t) {
    case 'focusin':
      return lt = pn(lt, e, t, n, r, l),
      !0;
    case 'dragenter':
      return it = pn(it, e, t, n, r, l),
      !0;
    case 'mouseover':
      return st = pn(st, e, t, n, r, l),
      !0;
    case 'pointerover':
      var i = l.pointerId;
      return In.set(i, pn(In.get(i) || null, e, t, n, r, l)),
      !0;
    case 'gotpointercapture':
      return i = l.pointerId,
      Fn.set(i, pn(Fn.get(i) || null, e, t, n, r, l)),
      !0
  }
  return !1
}
function Uu(e) {
  var t = kt(e.target);
  if (t !== null) {
    var n = Lt(t);
    if (n !== null) {
      if (t = n.tag, t === 13) {
        if (t = Eu(n), t !== null) {
          e.blockedOn = t,
          Fu(e.priority, function () {
            Du(n)
          });
          return
        }
      } else if (t === 3 && n.stateNode.current.memoizedState.isDehydrated) {
        e.blockedOn = n.tag === 3 ? n.stateNode.containerInfo : null;
        return
      }
    }
  }
  e.blockedOn = null
}
function Sr(e) {
  if (e.blockedOn !== null) return !1;
  for (var t = e.targetContainers; 0 < t.length; ) {
    var n = di(e.domEventName, e.eventSystemFlags, t[0], e.nativeEvent);
    if (n === null) {
      n = e.nativeEvent;
      var r = new n.constructor(n.type, n);
      ii = r,
      n.target.dispatchEvent(r),
      ii = null
    } else return t = bn(n),
    t !== null &&
    bi(t),
    e.blockedOn = n,
    !1;
    t.shift()
  }
  return !0
}
function Zs(e, t, n) {
  Sr(e) &&
  n.delete(t)
}
function ad() {
  ci = !1,
  lt !== null &&
  Sr(lt) &&
  (lt = null),
  it !== null &&
  Sr(it) &&
  (it = null),
  st !== null &&
  Sr(st) &&
  (st = null),
  In.forEach(Zs),
  Fn.forEach(Zs)
}
function mn(e, t) {
  e.blockedOn === t &&
  (
    e.blockedOn = null,
    ci ||
    (
      ci = !0,
      ge.unstable_scheduleCallback(ge.unstable_NormalPriority, ad)
    )
  )
}
function Un(e) {
  function t(l) {
    return mn(l, e)
  }
  if (0 < ar.length) {
    mn(ar[0], e);
    for (var n = 1; n < ar.length; n++) {
      var r = ar[n];
      r.blockedOn === e &&
      (r.blockedOn = null)
    }
  }
  for (
    lt !== null &&
    mn(lt, e),
    it !== null &&
    mn(it, e),
    st !== null &&
    mn(st, e),
    In.forEach(t),
    Fn.forEach(t),
    n = 0;
    n < et.length;
    n++
  ) r = et[n],
  r.blockedOn === e &&
  (r.blockedOn = null);
  for (; 0 < et.length && (n = et[0], n.blockedOn === null); ) Uu(n),
  n.blockedOn === null &&
  et.shift()
}
var Xt = Ze.ReactCurrentBatchConfig,
Fr = !0;
function cd(e, t, n, r) {
  var l = M,
  i = Xt.transition;
  Xt.transition = null;
  try {
    M = 1,
    es(e, t, n, r)
  } finally {
    M = l,
    Xt.transition = i
  }
}
function dd(e, t, n, r) {
  var l = M,
  i = Xt.transition;
  Xt.transition = null;
  try {
    M = 4,
    es(e, t, n, r)
  } finally {
    M = l,
    Xt.transition = i
  }
}
function es(e, t, n, r) {
  if (Fr) {
    var l = di(e, t, n, r);
    if (l === null) Il(e, t, r, Ur, n),
    Xs(e, r);
     else if (ud(l, e, t, n, r)) r.stopPropagation();
     else if (Xs(e, r), t & 4 && - 1 < od.indexOf(e)) {
      for (; l !== null; ) {
        var i = bn(l);
        if (i !== null && Ou(i), i = di(e, t, n, r), i === null && Il(e, t, r, Ur, n), i === l) break;
        l = i
      }
      l !== null &&
      r.stopPropagation()
    } else Il(e, t, r, null, n)
  }
}
var Ur = null;
function di(e, t, n, r) {
  if (Ur = null, e = Zi(r), e = kt(e), e !== null) if (t = Lt(e), t === null) e = null;
   else if (n = t.tag, n === 13) {
    if (e = Eu(t), e !== null) return e;
    e = null
  } else if (n === 3) {
    if (t.stateNode.current.memoizedState.isDehydrated) return t.tag === 3 ? t.stateNode.containerInfo : null;
    e = null
  } else t !== e &&
  (e = null);
  return Ur = e,
  null
}
function Au(e) {
  switch (e) {
    case 'cancel':
    case 'click':
    case 'close':
    case 'contextmenu':
    case 'copy':
    case 'cut':
    case 'auxclick':
    case 'dblclick':
    case 'dragend':
    case 'dragstart':
    case 'drop':
    case 'focusin':
    case 'focusout':
    case 'input':
    case 'invalid':
    case 'keydown':
    case 'keypress':
    case 'keyup':
    case 'mousedown':
    case 'mouseup':
    case 'paste':
    case 'pause':
    case 'play':
    case 'pointercancel':
    case 'pointerdown':
    case 'pointerup':
    case 'ratechange':
    case 'reset':
    case 'resize':
    case 'seeked':
    case 'submit':
    case 'touchcancel':
    case 'touchend':
    case 'touchstart':
    case 'volumechange':
    case 'change':
    case 'selectionchange':
    case 'textInput':
    case 'compositionstart':
    case 'compositionend':
    case 'compositionupdate':
    case 'beforeblur':
    case 'afterblur':
    case 'beforeinput':
    case 'blur':
    case 'fullscreenchange':
    case 'focus':
    case 'hashchange':
    case 'popstate':
    case 'select':
    case 'selectstart':
      return 1;
    case 'drag':
    case 'dragenter':
    case 'dragexit':
    case 'dragleave':
    case 'dragover':
    case 'mousemove':
    case 'mouseout':
    case 'mouseover':
    case 'pointermove':
    case 'pointerout':
    case 'pointerover':
    case 'scroll':
    case 'toggle':
    case 'touchmove':
    case 'wheel':
    case 'mouseenter':
    case 'mouseleave':
    case 'pointerenter':
    case 'pointerleave':
      return 4;
    case 'message':
      switch (qc()) {
        case Ji:
          return 1;
        case zu:
          return 4;
        case Dr:
        case bc:
          return 16;
        case Tu:
          return 536870912;
        default:
          return 16
      }
    default:
      return 16
  }
}
var nt = null,
ts = null,
Nr = null;
function $u() {
  if (Nr) return Nr;
  var e,
  t = ts,
  n = t.length,
  r,
  l = 'value' in nt ? nt.value : nt.textContent,
  i = l.length;
  for (e = 0; e < n && t[e] === l[e]; e++);
  var s = n - e;
  for (r = 1; r <= s && t[n - r] === l[i - r]; r++);
  return Nr = l.slice(e, 1 < r ? 1 - r : void 0)
}
function jr(e) {
  var t = e.keyCode;
  return 'charCode' in e ? (e = e.charCode, e === 0 && t === 13 && (e = 13)) : e = t,
  e === 10 &&
  (e = 13),
  32 <= e ||
  e === 13 ? e : 0
}
function cr() {
  return !0
}
function Js() {
  return !1
}
function we(e) {
  function t(n, r, l, i, s) {
    this._reactName = n,
    this._targetInst = l,
    this.type = r,
    this.nativeEvent = i,
    this.target = s,
    this.currentTarget = null;
    for (var u in e) e.hasOwnProperty(u) &&
    (n = e[u], this[u] = n ? n(i) : i[u]);
    return this.isDefaultPrevented = (
      i.defaultPrevented != null ? i.defaultPrevented : i.returnValue === !1
    ) ? cr : Js,
    this.isPropagationStopped = Js,
    this
  }
  return H(
    t.prototype,
    {
      preventDefault: function () {
        this.defaultPrevented = !0;
        var n = this.nativeEvent;
        n &&
        (
          n.preventDefault ? n.preventDefault() : typeof n.returnValue != 'unknown' &&
          (n.returnValue = !1),
          this.isDefaultPrevented = cr
        )
      },
      stopPropagation: function () {
        var n = this.nativeEvent;
        n &&
        (
          n.stopPropagation ? n.stopPropagation() : typeof n.cancelBubble != 'unknown' &&
          (n.cancelBubble = !0),
          this.isPropagationStopped = cr
        )
      },
      persist: function () {
      },
      isPersistent: cr
    }
  ),
  t
}
var on = {
  eventPhase: 0,
  bubbles: 0,
  cancelable: 0,
  timeStamp: function (e) {
    return e.timeStamp ||
    Date.now()
  },
  defaultPrevented: 0,
  isTrusted: 0
},
ns = we(on),
qn = H({
}, on, {
  view: 0,
  detail: 0
}),
fd = we(qn),
Pl,
_l,
hn,
ll = H({
}, qn, {
  screenX: 0,
  screenY: 0,
  clientX: 0,
  clientY: 0,
  pageX: 0,
  pageY: 0,
  ctrlKey: 0,
  shiftKey: 0,
  altKey: 0,
  metaKey: 0,
  getModifierState: rs,
  button: 0,
  buttons: 0,
  relatedTarget: function (e) {
    return e.relatedTarget === void 0 ? e.fromElement === e.srcElement ? e.toElement : e.fromElement : e.relatedTarget
  },
  movementX: function (e) {
    return 'movementX' in e ? e.movementX : (
      e !== hn &&
      (
        hn &&
        e.type === 'mousemove' ? (Pl = e.screenX - hn.screenX, _l = e.screenY - hn.screenY) : _l = Pl = 0,
        hn = e
      ),
      Pl
    )
  },
  movementY: function (e) {
    return 'movementY' in e ? e.movementY : _l
  }
}),
qs = we(ll),
pd = H({
}, ll, {
  dataTransfer: 0
}),
md = we(pd),
hd = H({
}, qn, {
  relatedTarget: 0
}),
Rl = we(hd),
vd = H({
}, on, {
  animationName: 0,
  elapsedTime: 0,
  pseudoElement: 0
}),
yd = we(vd),
gd = H({
}, on, {
  clipboardData: function (e) {
    return 'clipboardData' in e ? e.clipboardData : window.clipboardData
  }
}),
xd = we(gd),
wd = H({
}, on, {
  data: 0
}),
bs = we(wd),
kd = {
  Esc: 'Escape',
  Spacebar: ' ',
  Left: 'ArrowLeft',
  Up: 'ArrowUp',
  Right: 'ArrowRight',
  Down: 'ArrowDown',
  Del: 'Delete',
  Win: 'OS',
  Menu: 'ContextMenu',
  Apps: 'ContextMenu',
  Scroll: 'ScrollLock',
  MozPrintableKey: 'Unidentified'
},
Sd = {
  8: 'Backspace',
  9: 'Tab',
  12: 'Clear',
  13: 'Enter',
  16: 'Shift',
  17: 'Control',
  18: 'Alt',
  19: 'Pause',
  20: 'CapsLock',
  27: 'Escape',
  32: ' ',
  33: 'PageUp',
  34: 'PageDown',
  35: 'End',
  36: 'Home',
  37: 'ArrowLeft',
  38: 'ArrowUp',
  39: 'ArrowRight',
  40: 'ArrowDown',
  45: 'Insert',
  46: 'Delete',
  112: 'F1',
  113: 'F2',
  114: 'F3',
  115: 'F4',
  116: 'F5',
  117: 'F6',
  118: 'F7',
  119: 'F8',
  120: 'F9',
  121: 'F10',
  122: 'F11',
  123: 'F12',
  144: 'NumLock',
  145: 'ScrollLock',
  224: 'Meta'
},
Nd = {
  Alt: 'altKey',
  Control: 'ctrlKey',
  Meta: 'metaKey',
  Shift: 'shiftKey'
};
function jd(e) {
  var t = this.nativeEvent;
  return t.getModifierState ? t.getModifierState(e) : (e = Nd[e]) ? !!t[e] : !1
}
function rs() {
  return jd
}
var Cd = H({
}, qn, {
  key: function (e) {
    if (e.key) {
      var t = kd[e.key] ||
      e.key;
      if (t !== 'Unidentified') return t
    }
    return e.type === 'keypress' ? (e = jr(e), e === 13 ? 'Enter' : String.fromCharCode(e)) : e.type === 'keydown' ||
    e.type === 'keyup' ? Sd[e.keyCode] ||
    'Unidentified' : ''
  },
  code: 0,
  location: 0,
  ctrlKey: 0,
  shiftKey: 0,
  altKey: 0,
  metaKey: 0,
  repeat: 0,
  locale: 0,
  getModifierState: rs,
  charCode: function (e) {
    return e.type === 'keypress' ? jr(e) : 0
  },
  keyCode: function (e) {
    return e.type === 'keydown' ||
    e.type === 'keyup' ? e.keyCode : 0
  },
  which: function (e) {
    return e.type === 'keypress' ? jr(e) : e.type === 'keydown' ||
    e.type === 'keyup' ? e.keyCode : 0
  }
}),
Ed = we(Cd),
Pd = H({
}, ll, {
  pointerId: 0,
  width: 0,
  height: 0,
  pressure: 0,
  tangentialPressure: 0,
  tiltX: 0,
  tiltY: 0,
  twist: 0,
  pointerType: 0,
  isPrimary: 0
}),
eo = we(Pd),
_d = H({
}, qn, {
  touches: 0,
  targetTouches: 0,
  changedTouches: 0,
  altKey: 0,
  metaKey: 0,
  ctrlKey: 0,
  shiftKey: 0,
  getModifierState: rs
}),
Rd = we(_d),
zd = H({
}, on, {
  propertyName: 0,
  elapsedTime: 0,
  pseudoElement: 0
}),
Td = we(zd),
Ld = H({
}, ll, {
  deltaX: function (e) {
    return 'deltaX' in e ? e.deltaX : 'wheelDeltaX' in e ? - e.wheelDeltaX : 0
  },
  deltaY: function (e) {
    return 'deltaY' in e ? e.deltaY : 'wheelDeltaY' in e ? - e.wheelDeltaY : 'wheelDelta' in e ? - e.wheelDelta : 0
  },
  deltaZ: 0,
  deltaMode: 0
}),
Md = we(Ld),
Od = [
  9,
  13,
  27,
  32
],
ls = Ke &&
'CompositionEvent' in window,
En = null;
Ke &&
'documentMode' in document &&
(En = document.documentMode);
var Dd = Ke &&
'TextEvent' in window &&
!En,
Hu = Ke &&
(!ls || En && 8 < En && 11 >= En),
to = ' ',
no = !1;
function Vu(e, t) {
  switch (e) {
    case 'keyup':
      return Od.indexOf(t.keyCode) !== - 1;
    case 'keydown':
      return t.keyCode !== 229;
    case 'keypress':
    case 'mousedown':
    case 'focusout':
      return !0;
    default:
      return !1
  }
}
function Bu(e) {
  return e = e.detail,
  typeof e == 'object' &&
  'data' in e ? e.data : null
}
var It = !1;
function Id(e, t) {
  switch (e) {
    case 'compositionend':
      return Bu(t);
    case 'keypress':
      return t.which !== 32 ? null : (no = !0, to);
    case 'textInput':
      return e = t.data,
      e === to &&
      no ? null : e;
    default:
      return null
  }
}
function Fd(e, t) {
  if (It) return e === 'compositionend' ||
  !ls &&
  Vu(e, t) ? (e = $u(), Nr = ts = nt = null, It = !1, e) : null;
  switch (e) {
    case 'paste':
      return null;
    case 'keypress':
      if (!(t.ctrlKey || t.altKey || t.metaKey) || t.ctrlKey && t.altKey) {
        if (t.char && 1 < t.char.length) return t.char;
        if (t.which) return String.fromCharCode(t.which)
      }
      return null;
    case 'compositionend':
      return Hu &&
      t.locale !== 'ko' ? null : t.data;
    default:
      return null
  }
}
var Ud = {
  color: !0,
  date: !0,
  datetime: !0,
  'datetime-local': !0,
  email: !0,
  month: !0,
  number: !0,
  password: !0,
  range: !0,
  search: !0,
  tel: !0,
  text: !0,
  time: !0,
  url: !0,
  week: !0
};
function ro(e) {
  var t = e &&
  e.nodeName &&
  e.nodeName.toLowerCase();
  return t === 'input' ? !!Ud[e.type] : t === 'textarea'
}
function Wu(e, t, n, r) {
  ku(r),
  t = Ar(t, 'onChange'),
  0 < t.length &&
  (
    n = new ns('onChange', 'change', null, n, r),
    e.push({
      event: n,
      listeners: t
    })
  )
}
var Pn = null,
An = null;
function Ad(e) {
  ta(e, 0)
}
function il(e) {
  var t = At(e);
  if (mu(t)) return e
}
function $d(e, t) {
  if (e === 'change') return t
}
var Qu = !1;
if (Ke) {
  var zl;
  if (Ke) {
    var Tl = 'oninput' in document;
    if (!Tl) {
      var lo = document.createElement('div');
      lo.setAttribute('oninput', 'return;'),
      Tl = typeof lo.oninput == 'function'
    }
    zl = Tl
  } else zl = !1;
  Qu = zl &&
  (!document.documentMode || 9 < document.documentMode)
}
function io() {
  Pn &&
  (Pn.detachEvent('onpropertychange', Ku), An = Pn = null)
}
function Ku(e) {
  if (e.propertyName === 'value' && il(An)) {
    var t = [];
    Wu(t, An, e, Zi(e)),
    Cu(Ad, t)
  }
}
function Hd(e, t, n) {
  e === 'focusin' ? (io(), Pn = t, An = n, Pn.attachEvent('onpropertychange', Ku)) : e === 'focusout' &&
  io()
}
function Vd(e) {
  if (e === 'selectionchange' || e === 'keyup' || e === 'keydown') return il(An)
}
function Bd(e, t) {
  if (e === 'click') return il(t)
}
function Wd(e, t) {
  if (e === 'input' || e === 'change') return il(t)
}
function Qd(e, t) {
  return e === t &&
  (e !== 0 || 1 / e === 1 / t) ||
  e !== e &&
  t !== t
}
var Oe = typeof Object.is == 'function' ? Object.is : Qd;
function $n(e, t) {
  if (Oe(e, t)) return !0;
  if (typeof e != 'object' || e === null || typeof t != 'object' || t === null) return !1;
  var n = Object.keys(e),
  r = Object.keys(t);
  if (n.length !== r.length) return !1;
  for (r = 0; r < n.length; r++) {
    var l = n[r];
    if (!Gl.call(t, l) || !Oe(e[l], t[l])) return !1
  }
  return !0
}
function so(e) {
  for (; e && e.firstChild; ) e = e.firstChild;
  return e
}
function oo(e, t) {
  var n = so(e);
  e = 0;
  for (var r; n; ) {
    if (n.nodeType === 3) {
      if (r = e + n.textContent.length, e <= t && r >= t) return {
        node: n,
        offset: t - e
      };
      e = r
    }
    e: {
      for (; n; ) {
        if (n.nextSibling) {
          n = n.nextSibling;
          break e
        }
        n = n.parentNode
      }
      n = void 0
    }
    n = so(n)
  }
}
function Gu(e, t) {
  return e &&
  t ? e === t ? !0 : e &&
  e.nodeType === 3 ? !1 : t &&
  t.nodeType === 3 ? Gu(e, t.parentNode) : 'contains' in e ? e.contains(t) : e.compareDocumentPosition ? !!(e.compareDocumentPosition(t) & 16) : !1 : !1
}
function Yu() {
  for (var e = window, t = Lr(); t instanceof e.HTMLIFrameElement; ) {
    try {
      var n = typeof t.contentWindow.location.href == 'string'
    } catch {
      n = !1
    }
    if (n) e = t.contentWindow;
     else break;
    t = Lr(e.document)
  }
  return t
}
function is(e) {
  var t = e &&
  e.nodeName &&
  e.nodeName.toLowerCase();
  return t &&
  (
    t === 'input' &&
    (
      e.type === 'text' ||
      e.type === 'search' ||
      e.type === 'tel' ||
      e.type === 'url' ||
      e.type === 'password'
    ) ||
    t === 'textarea' ||
    e.contentEditable === 'true'
  )
}
function Kd(e) {
  var t = Yu(),
  n = e.focusedElem,
  r = e.selectionRange;
  if (
    t !== n &&
    n &&
    n.ownerDocument &&
    Gu(n.ownerDocument.documentElement, n)
  ) {
    if (r !== null && is(n)) {
      if (t = r.start, e = r.end, e === void 0 && (e = t), 'selectionStart' in n) n.selectionStart = t,
      n.selectionEnd = Math.min(e, n.value.length);
       else if (
        e = (t = n.ownerDocument || document) &&
        t.defaultView ||
        window,
        e.getSelection
      ) {
        e = e.getSelection();
        var l = n.textContent.length,
        i = Math.min(r.start, l);
        r = r.end === void 0 ? i : Math.min(r.end, l),
        !e.extend &&
        i > r &&
        (l = r, r = i, i = l),
        l = oo(n, i);
        var s = oo(n, r);
        l &&
        s &&
        (
          e.rangeCount !== 1 ||
          e.anchorNode !== l.node ||
          e.anchorOffset !== l.offset ||
          e.focusNode !== s.node ||
          e.focusOffset !== s.offset
        ) &&
        (
          t = t.createRange(),
          t.setStart(l.node, l.offset),
          e.removeAllRanges(),
          i > r ? (e.addRange(t), e.extend(s.node, s.offset)) : (t.setEnd(s.node, s.offset), e.addRange(t))
        )
      }
    }
    for (t = [], e = n; e = e.parentNode; ) e.nodeType === 1 &&
    t.push({
      element: e,
      left: e.scrollLeft,
      top: e.scrollTop
    });
    for (typeof n.focus == 'function' && n.focus(), n = 0; n < t.length; n++) e = t[n],
    e.element.scrollLeft = e.left,
    e.element.scrollTop = e.top
  }
}
var Gd = Ke &&
'documentMode' in document &&
11 >= document.documentMode,
Ft = null,
fi = null,
_n = null,
pi = !1;
function uo(e, t, n) {
  var r = n.window === n ? n.document : n.nodeType === 9 ? n : n.ownerDocument;
  pi ||
  Ft == null ||
  Ft !== Lr(r) ||
  (
    r = Ft,
    'selectionStart' in r &&
    is(r) ? r = {
      start: r.selectionStart,
      end: r.selectionEnd
    }
     : (
      r = (r.ownerDocument && r.ownerDocument.defaultView || window).getSelection(),
      r = {
        anchorNode: r.anchorNode,
        anchorOffset: r.anchorOffset,
        focusNode: r.focusNode,
        focusOffset: r.focusOffset
      }
    ),
    _n &&
    $n(_n, r) ||
    (
      _n = r,
      r = Ar(fi, 'onSelect'),
      0 < r.length &&
      (
        t = new ns('onSelect', 'select', null, t, n),
        e.push({
          event: t,
          listeners: r
        }),
        t.target = Ft
      )
    )
  )
}
function dr(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(),
  n['Webkit' + e] = 'webkit' + t,
  n['Moz' + e] = 'moz' + t,
  n
}
var Ut = {
  animationend: dr('Animation', 'AnimationEnd'),
  animationiteration: dr('Animation', 'AnimationIteration'),
  animationstart: dr('Animation', 'AnimationStart'),
  transitionend: dr('Transition', 'TransitionEnd')
},
Ll = {},
Xu = {};
Ke &&
(
  Xu = document.createElement('div').style,
  'AnimationEvent' in window ||
  (
    delete Ut.animationend.animation,
    delete Ut.animationiteration.animation,
    delete Ut.animationstart.animation
  ),
  'TransitionEvent' in window ||
  delete Ut.transitionend.transition
);
function sl(e) {
  if (Ll[e]) return Ll[e];
  if (!Ut[e]) return e;
  var t = Ut[e],
  n;
  for (n in t) if (t.hasOwnProperty(n) && n in Xu) return Ll[e] = t[n];
  return e
}
var Zu = sl('animationend'),
Ju = sl('animationiteration'),
qu = sl('animationstart'),
bu = sl('transitionend'),
ea = new Map,
ao = 'abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel'.split(' ');
function mt(e, t) {
  ea.set(e, t),
  Tt(t, [
    e
  ])
}
for (var Ml = 0; Ml < ao.length; Ml++) {
  var Ol = ao[Ml],
  Yd = Ol.toLowerCase(),
  Xd = Ol[0].toUpperCase() + Ol.slice(1);
  mt(Yd, 'on' + Xd)
}
mt(Zu, 'onAnimationEnd');
mt(Ju, 'onAnimationIteration');
mt(qu, 'onAnimationStart');
mt('dblclick', 'onDoubleClick');
mt('focusin', 'onFocus');
mt('focusout', 'onBlur');
mt(bu, 'onTransitionEnd');
qt('onMouseEnter', [
  'mouseout',
  'mouseover'
]);
qt('onMouseLeave', [
  'mouseout',
  'mouseover'
]);
qt('onPointerEnter', [
  'pointerout',
  'pointerover'
]);
qt('onPointerLeave', [
  'pointerout',
  'pointerover'
]);
Tt(
  'onChange',
  'change click focusin focusout input keydown keyup selectionchange'.split(' ')
);
Tt(
  'onSelect',
  'focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange'.split(' ')
);
Tt(
  'onBeforeInput',
  [
    'compositionend',
    'keypress',
    'textInput',
    'paste'
  ]
);
Tt(
  'onCompositionEnd',
  'compositionend focusout keydown keypress keyup mousedown'.split(' ')
);
Tt(
  'onCompositionStart',
  'compositionstart focusout keydown keypress keyup mousedown'.split(' ')
);
Tt(
  'onCompositionUpdate',
  'compositionupdate focusout keydown keypress keyup mousedown'.split(' ')
);
var Sn = 'abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting'.split(' '),
Zd = new Set(
  'cancel close invalid load scroll toggle'.split(' ').concat(Sn)
);
function co(e, t, n) {
  var r = e.type ||
  'unknown-event';
  e.currentTarget = n,
  Yc(r, t, void 0, e),
  e.currentTarget = null
}
function ta(e, t) {
  t = (t & 4) !== 0;
  for (var n = 0; n < e.length; n++) {
    var r = e[n],
    l = r.event;
    r = r.listeners;
    e: {
      var i = void 0;
      if (t) for (var s = r.length - 1; 0 <= s; s--) {
        var u = r[s],
        a = u.instance,
        d = u.currentTarget;
        if (u = u.listener, a !== i && l.isPropagationStopped()) break e;
        co(l, u, d),
        i = a
      } else for (s = 0; s < r.length; s++) {
        if (
          u = r[s],
          a = u.instance,
          d = u.currentTarget,
          u = u.listener,
          a !== i &&
          l.isPropagationStopped()
        ) break e;
        co(l, u, d),
        i = a
      }
    }
  }
  if (Or) throw e = ui,
  Or = !1,
  ui = null,
  e
}
function D(e, t) {
  var n = t[gi];
  n === void 0 &&
  (n = t[gi] = new Set);
  var r = e + '__bubble';
  n.has(r) ||
  (na(t, e, 2, !1), n.add(r))
}
function Dl(e, t, n) {
  var r = 0;
  t &&
  (r |= 4),
  na(n, e, r, t)
}
var fr = '_reactListening' + Math.random().toString(36).slice(2);
function Hn(e) {
  if (!e[fr]) {
    e[fr] = !0,
    au.forEach(
      function (n) {
        n !== 'selectionchange' &&
        (Zd.has(n) || Dl(n, !1, e), Dl(n, !0, e))
      }
    );
    var t = e.nodeType === 9 ? e : e.ownerDocument;
    t === null ||
    t[fr] ||
    (t[fr] = !0, Dl('selectionchange', !1, t))
  }
}
function na(e, t, n, r) {
  switch (Au(t)) {
    case 1:
      var l = cd;
      break;
    case 4:
      l = dd;
      break;
    default:
      l = es
  }
  n = l.bind(null, t, n, e),
  l = void 0,
  !oi ||
  t !== 'touchstart' &&
  t !== 'touchmove' &&
  t !== 'wheel' ||
  (l = !0),
  r ? l !== void 0 ? e.addEventListener(t, n, {
    capture: !0,
    passive: l
  }) : e.addEventListener(t, n, !0) : l !== void 0 ? e.addEventListener(t, n, {
    passive: l
  }) : e.addEventListener(t, n, !1)
}
function Il(e, t, n, r, l) {
  var i = r;
  if (!(t & 1) && !(t & 2) && r !== null) e: for (; ; ) {
    if (r === null) return;
    var s = r.tag;
    if (s === 3 || s === 4) {
      var u = r.stateNode.containerInfo;
      if (u === l || u.nodeType === 8 && u.parentNode === l) break;
      if (s === 4) for (s = r.return; s !== null; ) {
        var a = s.tag;
        if (
          (a === 3 || a === 4) &&
          (
            a = s.stateNode.containerInfo,
            a === l ||
            a.nodeType === 8 &&
            a.parentNode === l
          )
        ) return;
        s = s.return
      }
      for (; u !== null; ) {
        if (s = kt(u), s === null) return;
        if (a = s.tag, a === 5 || a === 6) {
          r = i = s;
          continue e
        }
        u = u.parentNode
      }
    }
    r = r.return
  }
  Cu(
    function () {
      var d = i,
      v = Zi(n),
      h = [];
      e: {
        var m = ea.get(e);
        if (m !== void 0) {
          var x = ns,
          w = e;
          switch (e) {
            case 'keypress':
              if (jr(n) === 0) break e;
            case 'keydown':
            case 'keyup':
              x = Ed;
              break;
            case 'focusin':
              w = 'focus',
              x = Rl;
              break;
            case 'focusout':
              w = 'blur',
              x = Rl;
              break;
            case 'beforeblur':
            case 'afterblur':
              x = Rl;
              break;
            case 'click':
              if (n.button === 2) break e;
            case 'auxclick':
            case 'dblclick':
            case 'mousedown':
            case 'mousemove':
            case 'mouseup':
            case 'mouseout':
            case 'mouseover':
            case 'contextmenu':
              x = qs;
              break;
            case 'drag':
            case 'dragend':
            case 'dragenter':
            case 'dragexit':
            case 'dragleave':
            case 'dragover':
            case 'dragstart':
            case 'drop':
              x = md;
              break;
            case 'touchcancel':
            case 'touchend':
            case 'touchmove':
            case 'touchstart':
              x = Rd;
              break;
            case Zu:
            case Ju:
            case qu:
              x = yd;
              break;
            case bu:
              x = Td;
              break;
            case 'scroll':
              x = fd;
              break;
            case 'wheel':
              x = Md;
              break;
            case 'copy':
            case 'cut':
            case 'paste':
              x = xd;
              break;
            case 'gotpointercapture':
            case 'lostpointercapture':
            case 'pointercancel':
            case 'pointerdown':
            case 'pointermove':
            case 'pointerout':
            case 'pointerover':
            case 'pointerup':
              x = eo
          }
          var k = (t & 4) !== 0,
          F = !k &&
          e === 'scroll',
          f = k ? m !== null ? m + 'Capture' : null : m;
          k = [];
          for (var c = d, p; c !== null; ) {
            p = c;
            var y = p.stateNode;
            if (
              p.tag === 5 &&
              y !== null &&
              (p = y, f !== null && (y = Dn(c, f), y != null && k.push(Vn(c, y, p)))),
              F
            ) break;
            c = c.return
          }
          0 < k.length &&
          (m = new x(m, w, null, n, v), h.push({
            event: m,
            listeners: k
          }))
        }
      }
      if (!(t & 7)) {
        e: {
          if (
            m = e === 'mouseover' ||
            e === 'pointerover',
            x = e === 'mouseout' ||
            e === 'pointerout',
            m &&
            n !== ii &&
            (w = n.relatedTarget || n.fromElement) &&
            (kt(w) || w[Ge])
          ) break e;
          if (
            (x || m) &&
            (
              m = v.window === v ? v : (m = v.ownerDocument) ? m.defaultView ||
              m.parentWindow : window,
              x ? (
                w = n.relatedTarget ||
                n.toElement,
                x = d,
                w = w ? kt(w) : null,
                w !== null &&
                (F = Lt(w), w !== F || w.tag !== 5 && w.tag !== 6) &&
                (w = null)
              ) : (x = null, w = d),
              x !== w
            )
          ) {
            if (
              k = qs,
              y = 'onMouseLeave',
              f = 'onMouseEnter',
              c = 'mouse',
              (e === 'pointerout' || e === 'pointerover') &&
              (k = eo, y = 'onPointerLeave', f = 'onPointerEnter', c = 'pointer'),
              F = x == null ? m : At(x),
              p = w == null ? m : At(w),
              m = new k(y, c + 'leave', x, n, v),
              m.target = F,
              m.relatedTarget = p,
              y = null,
              kt(v) === d &&
              (k = new k(f, c + 'enter', w, n, v), k.target = p, k.relatedTarget = F, y = k),
              F = y,
              x &&
              w
            ) t: {
              for (k = x, f = w, c = 0, p = k; p; p = Mt(p)) c++;
              for (p = 0, y = f; y; y = Mt(y)) p++;
              for (; 0 < c - p; ) k = Mt(k),
              c--;
              for (; 0 < p - c; ) f = Mt(f),
              p--;
              for (; c--; ) {
                if (k === f || f !== null && k === f.alternate) break t;
                k = Mt(k),
                f = Mt(f)
              }
              k = null
            } else k = null;
            x !== null &&
            fo(h, m, x, k, !1),
            w !== null &&
            F !== null &&
            fo(h, F, w, k, !0)
          }
        }
        e: {
          if (
            m = d ? At(d) : window,
            x = m.nodeName &&
            m.nodeName.toLowerCase(),
            x === 'select' ||
            x === 'input' &&
            m.type === 'file'
          ) var N = $d;
           else if (ro(m)) if (Qu) N = Wd;
           else {
            N = Vd;
            var C = Hd
          } else (x = m.nodeName) &&
          x.toLowerCase() === 'input' &&
          (m.type === 'checkbox' || m.type === 'radio') &&
          (N = Bd);
          if (N && (N = N(e, d))) {
            Wu(h, N, n, v);
            break e
          }
          C &&
          C(e, m, d),
          e === 'focusout' &&
          (C = m._wrapperState) &&
          C.controlled &&
          m.type === 'number' &&
          ei(m, 'number', m.value)
        }
        switch (C = d ? At(d) : window, e) {
          case 'focusin':
            (ro(C) || C.contentEditable === 'true') &&
            (Ft = C, fi = d, _n = null);
            break;
          case 'focusout':
            _n = fi = Ft = null;
            break;
          case 'mousedown':
            pi = !0;
            break;
          case 'contextmenu':
          case 'mouseup':
          case 'dragend':
            pi = !1,
            uo(h, n, v);
            break;
          case 'selectionchange':
            if (Gd) break;
          case 'keydown':
          case 'keyup':
            uo(h, n, v)
        }
        var E;
        if (ls) e: {
          switch (e) {
            case 'compositionstart':
              var P = 'onCompositionStart';
              break e;
            case 'compositionend':
              P = 'onCompositionEnd';
              break e;
            case 'compositionupdate':
              P = 'onCompositionUpdate';
              break e
          }
          P = void 0
        } else It ? Vu(e, n) &&
        (P = 'onCompositionEnd') : e === 'keydown' &&
        n.keyCode === 229 &&
        (P = 'onCompositionStart');
        P &&
        (
          Hu &&
          n.locale !== 'ko' &&
          (
            It ||
            P !== 'onCompositionStart' ? P === 'onCompositionEnd' &&
            It &&
            (E = $u()) : (nt = v, ts = 'value' in nt ? nt.value : nt.textContent, It = !0)
          ),
          C = Ar(d, P),
          0 < C.length &&
          (
            P = new bs(P, e, null, n, v),
            h.push({
              event: P,
              listeners: C
            }),
            E ? P.data = E : (E = Bu(n), E !== null && (P.data = E))
          )
        ),
        (E = Dd ? Id(e, n) : Fd(e, n)) &&
        (
          d = Ar(d, 'onBeforeInput'),
          0 < d.length &&
          (
            v = new bs('onBeforeInput', 'beforeinput', null, n, v),
            h.push({
              event: v,
              listeners: d
            }),
            v.data = E
          )
        )
      }
      ta(h, t)
    }
  )
}
function Vn(e, t, n) {
  return {
    instance: e,
    listener: t,
    currentTarget: n
  }
}
function Ar(e, t) {
  for (var n = t + 'Capture', r = []; e !== null; ) {
    var l = e,
    i = l.stateNode;
    l.tag === 5 &&
    i !== null &&
    (
      l = i,
      i = Dn(e, n),
      i != null &&
      r.unshift(Vn(e, i, l)),
      i = Dn(e, t),
      i != null &&
      r.push(Vn(e, i, l))
    ),
    e = e.return
  }
  return r
}
function Mt(e) {
  if (e === null) return null;
  do e = e.return;
  while (e && e.tag !== 5);
  return e ||
  null
}
function fo(e, t, n, r, l) {
  for (var i = t._reactName, s = []; n !== null && n !== r; ) {
    var u = n,
    a = u.alternate,
    d = u.stateNode;
    if (a !== null && a === r) break;
    u.tag === 5 &&
    d !== null &&
    (
      u = d,
      l ? (a = Dn(n, i), a != null && s.unshift(Vn(n, a, u))) : l ||
      (a = Dn(n, i), a != null && s.push(Vn(n, a, u)))
    ),
    n = n.return
  }
  s.length !== 0 &&
  e.push({
    event: t,
    listeners: s
  })
}
var Jd = /\r\n?/g,
qd = /\u0000|\uFFFD/g;
function po(e) {
  return (typeof e == 'string' ? e : '' + e).replace(Jd, `

  `).replace(qd, '')
}
function pr(e, t, n) {
  if (t = po(t), po(e) !== t && n) throw Error(g(425))
}
function $r() {
}
var mi = null,
hi = null;
function vi(e, t) {
  return e === 'textarea' ||
  e === 'noscript' ||
  typeof t.children == 'string' ||
  typeof t.children == 'number' ||
  typeof t.dangerouslySetInnerHTML == 'object' &&
  t.dangerouslySetInnerHTML !== null &&
  t.dangerouslySetInnerHTML.__html != null
}
var yi = typeof setTimeout == 'function' ? setTimeout : void 0,
bd = typeof clearTimeout == 'function' ? clearTimeout : void 0,
mo = typeof Promise == 'function' ? Promise : void 0,
ef = typeof queueMicrotask == 'function' ? queueMicrotask : typeof mo < 'u' ? function (e) {
  return mo.resolve(null).then(e).catch(tf)
}
 : yi;
function tf(e) {
  setTimeout(function () {
    throw e
  })
}
function Fl(e, t) {
  var n = t,
  r = 0;
  do {
    var l = n.nextSibling;
    if (e.removeChild(n), l && l.nodeType === 8) if (n = l.data, n === '/$') {
      if (r === 0) {
        e.removeChild(l),
        Un(t);
        return
      }
      r--
    } else n !== '$' &&
    n !== '$?' &&
    n !== '$!' ||
    r++;
    n = l
  } while (n);
  Un(t)
}
function ot(e) {
  for (; e != null; e = e.nextSibling) {
    var t = e.nodeType;
    if (t === 1 || t === 3) break;
    if (t === 8) {
      if (t = e.data, t === '$' || t === '$!' || t === '$?') break;
      if (t === '/$') return null
    }
  }
  return e
}
function ho(e) {
  e = e.previousSibling;
  for (var t = 0; e; ) {
    if (e.nodeType === 8) {
      var n = e.data;
      if (n === '$' || n === '$!' || n === '$?') {
        if (t === 0) return e;
        t--
      } else n === '/$' &&
      t++
    }
    e = e.previousSibling
  }
  return null
}
var un = Math.random().toString(36).slice(2),
Fe = '__reactFiber$' + un,
Bn = '__reactProps$' + un,
Ge = '__reactContainer$' + un,
gi = '__reactEvents$' + un,
nf = '__reactListeners$' + un,
rf = '__reactHandles$' + un;
function kt(e) {
  var t = e[Fe];
  if (t) return t;
  for (var n = e.parentNode; n; ) {
    if (t = n[Ge] || n[Fe]) {
      if (n = t.alternate, t.child !== null || n !== null && n.child !== null) for (e = ho(e); e !== null; ) {
        if (n = e[Fe]) return n;
        e = ho(e)
      }
      return t
    }
    e = n,
    n = e.parentNode
  }
  return null
}
function bn(e) {
  return e = e[Fe] ||
  e[Ge],
  !e ||
  e.tag !== 5 &&
  e.tag !== 6 &&
  e.tag !== 13 &&
  e.tag !== 3 ? null : e
}
function At(e) {
  if (e.tag === 5 || e.tag === 6) return e.stateNode;
  throw Error(g(33))
}
function ol(e) {
  return e[Bn] ||
  null
}
var xi = [],
$t = - 1;
function ht(e) {
  return {
    current: e
  }
}
function I(e) {
  0 > $t ||
  (e.current = xi[$t], xi[$t] = null, $t--)
}
function O(e, t) {
  $t++,
  xi[$t] = e.current,
  e.current = t
}
var pt = {},
ie = ht(pt),
fe = ht(!1),
Et = pt;
function bt(e, t) {
  var n = e.type.contextTypes;
  if (!n) return pt;
  var r = e.stateNode;
  if (r && r.__reactInternalMemoizedUnmaskedChildContext === t) return r.__reactInternalMemoizedMaskedChildContext;
  var l = {},
  i;
  for (i in n) l[i] = t[i];
  return r &&
  (
    e = e.stateNode,
    e.__reactInternalMemoizedUnmaskedChildContext = t,
    e.__reactInternalMemoizedMaskedChildContext = l
  ),
  l
}
function pe(e) {
  return e = e.childContextTypes,
  e != null
}
function Hr() {
  I(fe),
  I(ie)
}
function vo(e, t, n) {
  if (ie.current !== pt) throw Error(g(168));
  O(ie, t),
  O(fe, n)
}
function ra(e, t, n) {
  var r = e.stateNode;
  if (t = t.childContextTypes, typeof r.getChildContext != 'function') return n;
  r = r.getChildContext();
  for (var l in r) if (!(l in t)) throw Error(g(108, Hc(e) || 'Unknown', l));
  return H({
  }, n, r)
}
function Vr(e) {
  return e = (e = e.stateNode) &&
  e.__reactInternalMemoizedMergedChildContext ||
  pt,
  Et = ie.current,
  O(ie, e),
  O(fe, fe.current),
  !0
}
function yo(e, t, n) {
  var r = e.stateNode;
  if (!r) throw Error(g(169));
  n ? (
    e = ra(e, t, Et),
    r.__reactInternalMemoizedMergedChildContext = e,
    I(fe),
    I(ie),
    O(ie, e)
  ) : I(fe),
  O(fe, n)
}
var Ve = null,
ul = !1,
Ul = !1;
function la(e) {
  Ve === null ? Ve = [
    e
  ] : Ve.push(e)
}
function lf(e) {
  ul = !0,
  la(e)
}
function vt() {
  if (!Ul && Ve !== null) {
    Ul = !0;
    var e = 0,
    t = M;
    try {
      var n = Ve;
      for (M = 1; e < n.length; e++) {
        var r = n[e];
        do r = r(!0);
        while (r !== null)
      }
      Ve = null,
      ul = !1
    } catch (l) {
      throw Ve !== null &&
      (Ve = Ve.slice(e + 1)),
      Ru(Ji, vt),
      l
    } finally {
      M = t,
      Ul = !1
    }
  }
  return null
}
var Ht = [],
Vt = 0,
Br = null,
Wr = 0,
ke = [],
Se = 0,
Pt = null,
Be = 1,
We = '';
function xt(e, t) {
  Ht[Vt++] = Wr,
  Ht[Vt++] = Br,
  Br = e,
  Wr = t
}
function ia(e, t, n) {
  ke[Se++] = Be,
  ke[Se++] = We,
  ke[Se++] = Pt,
  Pt = e;
  var r = Be;
  e = We;
  var l = 32 - Le(r) - 1;
  r &= ~(1 << l),
  n += 1;
  var i = 32 - Le(t) + l;
  if (30 < i) {
    var s = l - l % 5;
    i = (r & (1 << s) - 1).toString(32),
    r >>= s,
    l -= s,
    Be = 1 << 32 - Le(t) + l | n << l | r,
    We = i + e
  } else Be = 1 << i | n << l | r,
  We = e
}
function ss(e) {
  e.return !== null &&
  (xt(e, 1), ia(e, 1, 0))
}
function os(e) {
  for (; e === Br; ) Br = Ht[--Vt],
  Ht[Vt] = null,
  Wr = Ht[--Vt],
  Ht[Vt] = null;
  for (; e === Pt; ) Pt = ke[--Se],
  ke[Se] = null,
  We = ke[--Se],
  ke[Se] = null,
  Be = ke[--Se],
  ke[Se] = null
}
var ye = null,
ve = null,
U = !1,
Te = null;
function sa(e, t) {
  var n = Ne(5, null, null, 0);
  n.elementType = 'DELETED',
  n.stateNode = t,
  n.return = e,
  t = e.deletions,
  t === null ? (e.deletions = [
    n
  ], e.flags |= 16) : t.push(n)
}
function go(e, t) {
  switch (e.tag) {
    case 5:
      var n = e.type;
      return t = t.nodeType !== 1 ||
      n.toLowerCase() !== t.nodeName.toLowerCase() ? null : t,
      t !== null ? (e.stateNode = t, ye = e, ve = ot(t.firstChild), !0) : !1;
    case 6:
      return t = e.pendingProps === '' ||
      t.nodeType !== 3 ? null : t,
      t !== null ? (e.stateNode = t, ye = e, ve = null, !0) : !1;
    case 13:
      return t = t.nodeType !== 8 ? null : t,
      t !== null ? (
        n = Pt !== null ? {
          id: Be,
          overflow: We
        }
         : null,
        e.memoizedState = {
          dehydrated: t,
          treeContext: n,
          retryLane: 1073741824
        },
        n = Ne(18, null, null, 0),
        n.stateNode = t,
        n.return = e,
        e.child = n,
        ye = e,
        ve = null,
        !0
      ) : !1;
    default:
      return !1
  }
}
function wi(e) {
  return (e.mode & 1) !== 0 &&
  (e.flags & 128) === 0
}
function ki(e) {
  if (U) {
    var t = ve;
    if (t) {
      var n = t;
      if (!go(e, t)) {
        if (wi(e)) throw Error(g(418));
        t = ot(n.nextSibling);
        var r = ye;
        t &&
        go(e, t) ? sa(r, n) : (e.flags = e.flags & - 4097 | 2, U = !1, ye = e)
      }
    } else {
      if (wi(e)) throw Error(g(418));
      e.flags = e.flags & - 4097 | 2,
      U = !1,
      ye = e
    }
  }
}
function xo(e) {
  for (e = e.return; e !== null && e.tag !== 5 && e.tag !== 3 && e.tag !== 13; ) e = e.return;
  ye = e
}
function mr(e) {
  if (e !== ye) return !1;
  if (!U) return xo(e),
  U = !0,
  !1;
  var t;
  if (
    (t = e.tag !== 3) &&
    !(t = e.tag !== 5) &&
    (
      t = e.type,
      t = t !== 'head' &&
      t !== 'body' &&
      !vi(e.type, e.memoizedProps)
    ),
    t &&
    (t = ve)
  ) {
    if (wi(e)) throw oa(),
    Error(g(418));
    for (; t; ) sa(e, t),
    t = ot(t.nextSibling)
  }
  if (xo(e), e.tag === 13) {
    if (e = e.memoizedState, e = e !== null ? e.dehydrated : null, !e) throw Error(g(317));
    e: {
      for (e = e.nextSibling, t = 0; e; ) {
        if (e.nodeType === 8) {
          var n = e.data;
          if (n === '/$') {
            if (t === 0) {
              ve = ot(e.nextSibling);
              break e
            }
            t--
          } else n !== '$' &&
          n !== '$!' &&
          n !== '$?' ||
          t++
        }
        e = e.nextSibling
      }
      ve = null
    }
  } else ve = ye ? ot(e.stateNode.nextSibling) : null;
  return !0
}
function oa() {
  for (var e = ve; e; ) e = ot(e.nextSibling)
}
function en() {
  ve = ye = null,
  U = !1
}
function us(e) {
  Te === null ? Te = [
    e
  ] : Te.push(e)
}
var sf = Ze.ReactCurrentBatchConfig;
function vn(e, t, n) {
  if (e = n.ref, e !== null && typeof e != 'function' && typeof e != 'object') {
    if (n._owner) {
      if (n = n._owner, n) {
        if (n.tag !== 1) throw Error(g(309));
        var r = n.stateNode
      }
      if (!r) throw Error(g(147, e));
      var l = r,
      i = '' + e;
      return t !== null &&
      t.ref !== null &&
      typeof t.ref == 'function' &&
      t.ref._stringRef === i ? t.ref : (
        t = function (s) {
          var u = l.refs;
          s === null ? delete u[i] : u[i] = s
        },
        t._stringRef = i,
        t
      )
    }
    if (typeof e != 'string') throw Error(g(284));
    if (!n._owner) throw Error(g(290, e))
  }
  return e
}
function hr(e, t) {
  throw e = Object.prototype.toString.call(t),
  Error(
    g(
      31,
      e === '[object Object]' ? 'object with keys {' + Object.keys(t).join(', ') + '}' : e
    )
  )
}
function wo(e) {
  var t = e._init;
  return t(e._payload)
}
function ua(e) {
  function t(f, c) {
    if (e) {
      var p = f.deletions;
      p === null ? (f.deletions = [
        c
      ], f.flags |= 16) : p.push(c)
    }
  }
  function n(f, c) {
    if (!e) return null;
    for (; c !== null; ) t(f, c),
    c = c.sibling;
    return null
  }
  function r(f, c) {
    for (f = new Map; c !== null; ) c.key !== null ? f.set(c.key, c) : f.set(c.index, c),
    c = c.sibling;
    return f
  }
  function l(f, c) {
    return f = dt(f, c),
    f.index = 0,
    f.sibling = null,
    f
  }
  function i(f, c, p) {
    return f.index = p,
    e ? (
      p = f.alternate,
      p !== null ? (p = p.index, p < c ? (f.flags |= 2, c) : p) : (f.flags |= 2, c)
    ) : (f.flags |= 1048576, c)
  }
  function s(f) {
    return e &&
    f.alternate === null &&
    (f.flags |= 2),
    f
  }
  function u(f, c, p, y) {
    return c === null ||
    c.tag !== 6 ? (c = Ql(p, f.mode, y), c.return = f, c) : (c = l(c, p), c.return = f, c)
  }
  function a(f, c, p, y) {
    var N = p.type;
    return N === Dt ? v(f, c, p.props.children, y, p.key) : c !== null &&
    (
      c.elementType === N ||
      typeof N == 'object' &&
      N !== null &&
      N.$$typeof === qe &&
      wo(N) === c.type
    ) ? (y = l(c, p.props), y.ref = vn(f, c, p), y.return = f, y) : (
      y = Tr(p.type, p.key, p.props, null, f.mode, y),
      y.ref = vn(f, c, p),
      y.return = f,
      y
    )
  }
  function d(f, c, p, y) {
    return c === null ||
    c.tag !== 4 ||
    c.stateNode.containerInfo !== p.containerInfo ||
    c.stateNode.implementation !== p.implementation ? (c = Kl(p, f.mode, y), c.return = f, c) : (c = l(c, p.children || []), c.return = f, c)
  }
  function v(f, c, p, y, N) {
    return c === null ||
    c.tag !== 7 ? (c = Ct(p, f.mode, y, N), c.return = f, c) : (c = l(c, p), c.return = f, c)
  }
  function h(f, c, p) {
    if (typeof c == 'string' && c !== '' || typeof c == 'number') return c = Ql('' + c, f.mode, p),
    c.return = f,
    c;
    if (typeof c == 'object' && c !== null) {
      switch (c.$$typeof) {
        case lr:
          return p = Tr(c.type, c.key, c.props, null, f.mode, p),
          p.ref = vn(f, null, c),
          p.return = f,
          p;
        case Ot:
          return c = Kl(c, f.mode, p),
          c.return = f,
          c;
        case qe:
          var y = c._init;
          return h(f, y(c._payload), p)
      }
      if (wn(c) || dn(c)) return c = Ct(c, f.mode, p, null),
      c.return = f,
      c;
      hr(f, c)
    }
    return null
  }
  function m(f, c, p, y) {
    var N = c !== null ? c.key : null;
    if (typeof p == 'string' && p !== '' || typeof p == 'number') return N !== null ? null : u(f, c, '' + p, y);
    if (typeof p == 'object' && p !== null) {
      switch (p.$$typeof) {
        case lr:
          return p.key === N ? a(f, c, p, y) : null;
        case Ot:
          return p.key === N ? d(f, c, p, y) : null;
        case qe:
          return N = p._init,
          m(f, c, N(p._payload), y)
      }
      if (wn(p) || dn(p)) return N !== null ? null : v(f, c, p, y, null);
      hr(f, p)
    }
    return null
  }
  function x(f, c, p, y, N) {
    if (typeof y == 'string' && y !== '' || typeof y == 'number') return f = f.get(p) ||
    null,
    u(c, f, '' + y, N);
    if (typeof y == 'object' && y !== null) {
      switch (y.$$typeof) {
        case lr:
          return f = f.get(y.key === null ? p : y.key) ||
          null,
          a(c, f, y, N);
        case Ot:
          return f = f.get(y.key === null ? p : y.key) ||
          null,
          d(c, f, y, N);
        case qe:
          var C = y._init;
          return x(f, c, p, C(y._payload), N)
      }
      if (wn(y) || dn(y)) return f = f.get(p) ||
      null,
      v(c, f, y, N, null);
      hr(c, y)
    }
    return null
  }
  function w(f, c, p, y) {
    for (var N = null, C = null, E = c, P = c = 0, B = null; E !== null && P < p.length; P++) {
      E.index > P ? (B = E, E = null) : B = E.sibling;
      var T = m(f, E, p[P], y);
      if (T === null) {
        E === null &&
        (E = B);
        break
      }
      e &&
      E &&
      T.alternate === null &&
      t(f, E),
      c = i(T, c, P),
      C === null ? N = T : C.sibling = T,
      C = T,
      E = B
    }
    if (P === p.length) return n(f, E),
    U &&
    xt(f, P),
    N;
    if (E === null) {
      for (; P < p.length; P++) E = h(f, p[P], y),
      E !== null &&
      (c = i(E, c, P), C === null ? N = E : C.sibling = E, C = E);
      return U &&
      xt(f, P),
      N
    }
    for (E = r(f, E); P < p.length; P++) B = x(E, f, P, p[P], y),
    B !== null &&
    (
      e &&
      B.alternate !== null &&
      E.delete(B.key === null ? P : B.key),
      c = i(B, c, P),
      C === null ? N = B : C.sibling = B,
      C = B
    );
    return e &&
    E.forEach(function (Pe) {
      return t(f, Pe)
    }),
    U &&
    xt(f, P),
    N
  }
  function k(f, c, p, y) {
    var N = dn(p);
    if (typeof N != 'function') throw Error(g(150));
    if (p = N.call(p), p == null) throw Error(g(151));
    for (
      var C = N = null,
      E = c,
      P = c = 0,
      B = null,
      T = p.next();
      E !== null &&
      !T.done;
      P++,
      T = p.next()
    ) {
      E.index > P ? (B = E, E = null) : B = E.sibling;
      var Pe = m(f, E, T.value, y);
      if (Pe === null) {
        E === null &&
        (E = B);
        break
      }
      e &&
      E &&
      Pe.alternate === null &&
      t(f, E),
      c = i(Pe, c, P),
      C === null ? N = Pe : C.sibling = Pe,
      C = Pe,
      E = B
    }
    if (T.done) return n(f, E),
    U &&
    xt(f, P),
    N;
    if (E === null) {
      for (; !T.done; P++, T = p.next()) T = h(f, T.value, y),
      T !== null &&
      (c = i(T, c, P), C === null ? N = T : C.sibling = T, C = T);
      return U &&
      xt(f, P),
      N
    }
    for (E = r(f, E); !T.done; P++, T = p.next()) T = x(E, f, P, T.value, y),
    T !== null &&
    (
      e &&
      T.alternate !== null &&
      E.delete(T.key === null ? P : T.key),
      c = i(T, c, P),
      C === null ? N = T : C.sibling = T,
      C = T
    );
    return e &&
    E.forEach(function (an) {
      return t(f, an)
    }),
    U &&
    xt(f, P),
    N
  }
  function F(f, c, p, y) {
    if (
      typeof p == 'object' &&
      p !== null &&
      p.type === Dt &&
      p.key === null &&
      (p = p.props.children),
      typeof p == 'object' &&
      p !== null
    ) {
      switch (p.$$typeof) {
        case lr:
          e: {
            for (var N = p.key, C = c; C !== null; ) {
              if (C.key === N) {
                if (N = p.type, N === Dt) {
                  if (C.tag === 7) {
                    n(f, C.sibling),
                    c = l(C, p.props.children),
                    c.return = f,
                    f = c;
                    break e
                  }
                } else if (
                  C.elementType === N ||
                  typeof N == 'object' &&
                  N !== null &&
                  N.$$typeof === qe &&
                  wo(N) === C.type
                ) {
                  n(f, C.sibling),
                  c = l(C, p.props),
                  c.ref = vn(f, C, p),
                  c.return = f,
                  f = c;
                  break e
                }
                n(f, C);
                break
              } else t(f, C);
              C = C.sibling
            }
            p.type === Dt ? (c = Ct(p.props.children, f.mode, y, p.key), c.return = f, f = c) : (
              y = Tr(p.type, p.key, p.props, null, f.mode, y),
              y.ref = vn(f, c, p),
              y.return = f,
              f = y
            )
          }
          return s(f);
        case Ot:
          e: {
            for (C = p.key; c !== null; ) {
              if (c.key === C) if (
                c.tag === 4 &&
                c.stateNode.containerInfo === p.containerInfo &&
                c.stateNode.implementation === p.implementation
              ) {
                n(f, c.sibling),
                c = l(c, p.children || []),
                c.return = f,
                f = c;
                break e
              } else {
                n(f, c);
                break
              } else t(f, c);
              c = c.sibling
            }
            c = Kl(p, f.mode, y),
            c.return = f,
            f = c
          }
          return s(f);
        case qe:
          return C = p._init,
          F(f, c, C(p._payload), y)
      }
      if (wn(p)) return w(f, c, p, y);
      if (dn(p)) return k(f, c, p, y);
      hr(f, p)
    }
    return typeof p == 'string' &&
    p !== '' ||
    typeof p == 'number' ? (
      p = '' + p,
      c !== null &&
      c.tag === 6 ? (n(f, c.sibling), c = l(c, p), c.return = f, f = c) : (n(f, c), c = Ql(p, f.mode, y), c.return = f, f = c),
      s(f)
    ) : n(f, c)
  }
  return F
}
var tn = ua(!0),
aa = ua(!1),
Qr = ht(null),
Kr = null,
Bt = null,
as = null;
function cs() {
  as = Bt = Kr = null
}
function ds(e) {
  var t = Qr.current;
  I(Qr),
  e._currentValue = t
}
function Si(e, t, n) {
  for (; e !== null; ) {
    var r = e.alternate;
    if (
      (e.childLanes & t) !== t ? (e.childLanes |= t, r !== null && (r.childLanes |= t)) : r !== null &&
      (r.childLanes & t) !== t &&
      (r.childLanes |= t),
      e === n
    ) break;
    e = e.return
  }
}
function Zt(e, t) {
  Kr = e,
  as = Bt = null,
  e = e.dependencies,
  e !== null &&
  e.firstContext !== null &&
  (e.lanes & t && (de = !0), e.firstContext = null)
}
function Ce(e) {
  var t = e._currentValue;
  if (as !== e) if (e = {
    context: e,
    memoizedValue: t,
    next: null
  }, Bt === null) {
    if (Kr === null) throw Error(g(308));
    Bt = e,
    Kr.dependencies = {
      lanes: 0,
      firstContext: e
    }
  } else Bt = Bt.next = e;
  return t
}
var St = null;
function fs(e) {
  St === null ? St = [
    e
  ] : St.push(e)
}
function ca(e, t, n, r) {
  var l = t.interleaved;
  return l === null ? (n.next = n, fs(t)) : (n.next = l.next, l.next = n),
  t.interleaved = n,
  Ye(e, r)
}
function Ye(e, t) {
  e.lanes |= t;
  var n = e.alternate;
  for (n !== null && (n.lanes |= t), n = e, e = e.return; e !== null; ) e.childLanes |= t,
  n = e.alternate,
  n !== null &&
  (n.childLanes |= t),
  n = e,
  e = e.return;
  return n.tag === 3 ? n.stateNode : null
}
var be = !1;
function ps(e) {
  e.updateQueue = {
    baseState: e.memoizedState,
    firstBaseUpdate: null,
    lastBaseUpdate: null,
    shared: {
      pending: null,
      interleaved: null,
      lanes: 0
    },
    effects: null
  }
}
function da(e, t) {
  e = e.updateQueue,
  t.updateQueue === e &&
  (
    t.updateQueue = {
      baseState: e.baseState,
      firstBaseUpdate: e.firstBaseUpdate,
      lastBaseUpdate: e.lastBaseUpdate,
      shared: e.shared,
      effects: e.effects
    }
  )
}
function Qe(e, t) {
  return {
    eventTime: e,
    lane: t,
    tag: 0,
    payload: null,
    callback: null,
    next: null
  }
}
function ut(e, t, n) {
  var r = e.updateQueue;
  if (r === null) return null;
  if (r = r.shared, L & 2) {
    var l = r.pending;
    return l === null ? t.next = t : (t.next = l.next, l.next = t),
    r.pending = t,
    Ye(e, n)
  }
  return l = r.interleaved,
  l === null ? (t.next = t, fs(r)) : (t.next = l.next, l.next = t),
  r.interleaved = t,
  Ye(e, n)
}
function Cr(e, t, n) {
  if (t = t.updateQueue, t !== null && (t = t.shared, (n & 4194240) !== 0)) {
    var r = t.lanes;
    r &= e.pendingLanes,
    n |= r,
    t.lanes = n,
    qi(e, n)
  }
}
function ko(e, t) {
  var n = e.updateQueue,
  r = e.alternate;
  if (r !== null && (r = r.updateQueue, n === r)) {
    var l = null,
    i = null;
    if (n = n.firstBaseUpdate, n !== null) {
      do {
        var s = {
          eventTime: n.eventTime,
          lane: n.lane,
          tag: n.tag,
          payload: n.payload,
          callback: n.callback,
          next: null
        };
        i === null ? l = i = s : i = i.next = s,
        n = n.next
      } while (n !== null);
      i === null ? l = i = t : i = i.next = t
    } else l = i = t;
    n = {
      baseState: r.baseState,
      firstBaseUpdate: l,
      lastBaseUpdate: i,
      shared: r.shared,
      effects: r.effects
    },
    e.updateQueue = n;
    return
  }
  e = n.lastBaseUpdate,
  e === null ? n.firstBaseUpdate = t : e.next = t,
  n.lastBaseUpdate = t
}
function Gr(e, t, n, r) {
  var l = e.updateQueue;
  be = !1;
  var i = l.firstBaseUpdate,
  s = l.lastBaseUpdate,
  u = l.shared.pending;
  if (u !== null) {
    l.shared.pending = null;
    var a = u,
    d = a.next;
    a.next = null,
    s === null ? i = d : s.next = d,
    s = a;
    var v = e.alternate;
    v !== null &&
    (
      v = v.updateQueue,
      u = v.lastBaseUpdate,
      u !== s &&
      (u === null ? v.firstBaseUpdate = d : u.next = d, v.lastBaseUpdate = a)
    )
  }
  if (i !== null) {
    var h = l.baseState;
    s = 0,
    v = d = a = null,
    u = i;
    do {
      var m = u.lane,
      x = u.eventTime;
      if ((r & m) === m) {
        v !== null &&
        (
          v = v.next = {
            eventTime: x,
            lane: 0,
            tag: u.tag,
            payload: u.payload,
            callback: u.callback,
            next: null
          }
        );
        e: {
          var w = e,
          k = u;
          switch (m = t, x = n, k.tag) {
            case 1:
              if (w = k.payload, typeof w == 'function') {
                h = w.call(x, h, m);
                break e
              }
              h = w;
              break e;
            case 3:
              w.flags = w.flags & - 65537 | 128;
            case 0:
              if (w = k.payload, m = typeof w == 'function' ? w.call(x, h, m) : w, m == null) break e;
              h = H({
              }, h, m);
              break e;
            case 2:
              be = !0
          }
        }
        u.callback !== null &&
        u.lane !== 0 &&
        (e.flags |= 64, m = l.effects, m === null ? l.effects = [
          u
        ] : m.push(u))
      } else x = {
        eventTime: x,
        lane: m,
        tag: u.tag,
        payload: u.payload,
        callback: u.callback,
        next: null
      },
      v === null ? (d = v = x, a = h) : v = v.next = x,
      s |= m;
      if (u = u.next, u === null) {
        if (u = l.shared.pending, u === null) break;
        m = u,
        u = m.next,
        m.next = null,
        l.lastBaseUpdate = m,
        l.shared.pending = null
      }
    } while (!0);
    if (
      v === null &&
      (a = h),
      l.baseState = a,
      l.firstBaseUpdate = d,
      l.lastBaseUpdate = v,
      t = l.shared.interleaved,
      t !== null
    ) {
      l = t;
      do s |= l.lane,
      l = l.next;
      while (l !== t)
    } else i === null &&
    (l.shared.lanes = 0);
    Rt |= s,
    e.lanes = s,
    e.memoizedState = h
  }
}
function So(e, t, n) {
  if (e = t.effects, t.effects = null, e !== null) for (t = 0; t < e.length; t++) {
    var r = e[t],
    l = r.callback;
    if (l !== null) {
      if (r.callback = null, r = n, typeof l != 'function') throw Error(g(191, l));
      l.call(r)
    }
  }
}
var er = {},
$e = ht(er),
Wn = ht(er),
Qn = ht(er);
function Nt(e) {
  if (e === er) throw Error(g(174));
  return e
}
function ms(e, t) {
  switch (O(Qn, t), O(Wn, e), O($e, er), e = t.nodeType, e) {
    case 9:
    case 11:
      t = (t = t.documentElement) ? t.namespaceURI : ni(null, '');
      break;
    default:
      e = e === 8 ? t.parentNode : t,
      t = e.namespaceURI ||
      null,
      e = e.tagName,
      t = ni(t, e)
  }
  I($e),
  O($e, t)
}
function nn() {
  I($e),
  I(Wn),
  I(Qn)
}
function fa(e) {
  Nt(Qn.current);
  var t = Nt($e.current),
  n = ni(t, e.type);
  t !== n &&
  (O(Wn, e), O($e, n))
}
function hs(e) {
  Wn.current === e &&
  (I($e), I(Wn))
}
var A = ht(0);
function Yr(e) {
  for (var t = e; t !== null; ) {
    if (t.tag === 13) {
      var n = t.memoizedState;
      if (
        n !== null &&
        (n = n.dehydrated, n === null || n.data === '$?' || n.data === '$!')
      ) return t
    } else if (t.tag === 19 && t.memoizedProps.revealOrder !== void 0) {
      if (t.flags & 128) return t
    } else if (t.child !== null) {
      t.child.return = t,
      t = t.child;
      continue
    }
    if (t === e) break;
    for (; t.sibling === null; ) {
      if (t.return === null || t.return === e) return null;
      t = t.return
    }
    t.sibling.return = t.return,
    t = t.sibling
  }
  return null
}
var Al = [];
function vs() {
  for (var e = 0; e < Al.length; e++) Al[e]._workInProgressVersionPrimary = null;
  Al.length = 0
}
var Er = Ze.ReactCurrentDispatcher,
$l = Ze.ReactCurrentBatchConfig,
_t = 0,
$ = null,
G = null,
Z = null,
Xr = !1,
Rn = !1,
Kn = 0,
of = 0;
function ne() {
  throw Error(g(321))
}
function ys(e, t) {
  if (t === null) return !1;
  for (var n = 0; n < t.length && n < e.length; n++) if (!Oe(e[n], t[n])) return !1;
  return !0
}
function gs(e, t, n, r, l, i) {
  if (
    _t = i,
    $ = t,
    t.memoizedState = null,
    t.updateQueue = null,
    t.lanes = 0,
    Er.current = e === null ||
    e.memoizedState === null ? df : ff,
    e = n(r, l),
    Rn
  ) {
    i = 0;
    do {
      if (Rn = !1, Kn = 0, 25 <= i) throw Error(g(301));
      i += 1,
      Z = G = null,
      t.updateQueue = null,
      Er.current = pf,
      e = n(r, l)
    } while (Rn)
  }
  if (
    Er.current = Zr,
    t = G !== null &&
    G.next !== null,
    _t = 0,
    Z = G = $ = null,
    Xr = !1,
    t
  ) throw Error(g(300));
  return e
}
function xs() {
  var e = Kn !== 0;
  return Kn = 0,
  e
}
function Ie() {
  var e = {
    memoizedState: null,
    baseState: null,
    baseQueue: null,
    queue: null,
    next: null
  };
  return Z === null ? $.memoizedState = Z = e : Z = Z.next = e,
  Z
}
function Ee() {
  if (G === null) {
    var e = $.alternate;
    e = e !== null ? e.memoizedState : null
  } else e = G.next;
  var t = Z === null ? $.memoizedState : Z.next;
  if (t !== null) Z = t,
  G = e;
   else {
    if (e === null) throw Error(g(310));
    G = e,
    e = {
      memoizedState: G.memoizedState,
      baseState: G.baseState,
      baseQueue: G.baseQueue,
      queue: G.queue,
      next: null
    },
    Z === null ? $.memoizedState = Z = e : Z = Z.next = e
  }
  return Z
}
function Gn(e, t) {
  return typeof t == 'function' ? t(e) : t
}
function Hl(e) {
  var t = Ee(),
  n = t.queue;
  if (n === null) throw Error(g(311));
  n.lastRenderedReducer = e;
  var r = G,
  l = r.baseQueue,
  i = n.pending;
  if (i !== null) {
    if (l !== null) {
      var s = l.next;
      l.next = i.next,
      i.next = s
    }
    r.baseQueue = l = i,
    n.pending = null
  }
  if (l !== null) {
    i = l.next,
    r = r.baseState;
    var u = s = null,
    a = null,
    d = i;
    do {
      var v = d.lane;
      if ((_t & v) === v) a !== null &&
      (
        a = a.next = {
          lane: 0,
          action: d.action,
          hasEagerState: d.hasEagerState,
          eagerState: d.eagerState,
          next: null
        }
      ),
      r = d.hasEagerState ? d.eagerState : e(r, d.action);
       else {
        var h = {
          lane: v,
          action: d.action,
          hasEagerState: d.hasEagerState,
          eagerState: d.eagerState,
          next: null
        };
        a === null ? (u = a = h, s = r) : a = a.next = h,
        $.lanes |= v,
        Rt |= v
      }
      d = d.next
    } while (d !== null && d !== i);
    a === null ? s = r : a.next = u,
    Oe(r, t.memoizedState) ||
    (de = !0),
    t.memoizedState = r,
    t.baseState = s,
    t.baseQueue = a,
    n.lastRenderedState = r
  }
  if (e = n.interleaved, e !== null) {
    l = e;
    do i = l.lane,
    $.lanes |= i,
    Rt |= i,
    l = l.next;
    while (l !== e)
  } else l === null &&
  (n.lanes = 0);
  return [t.memoizedState,
  n.dispatch]
}
function Vl(e) {
  var t = Ee(),
  n = t.queue;
  if (n === null) throw Error(g(311));
  n.lastRenderedReducer = e;
  var r = n.dispatch,
  l = n.pending,
  i = t.memoizedState;
  if (l !== null) {
    n.pending = null;
    var s = l = l.next;
    do i = e(i, s.action),
    s = s.next;
    while (s !== l);
    Oe(i, t.memoizedState) ||
    (de = !0),
    t.memoizedState = i,
    t.baseQueue === null &&
    (t.baseState = i),
    n.lastRenderedState = i
  }
  return [i,
  r]
}
function pa() {
}
function ma(e, t) {
  var n = $,
  r = Ee(),
  l = t(),
  i = !Oe(r.memoizedState, l);
  if (
    i &&
    (r.memoizedState = l, de = !0),
    r = r.queue,
    ws(ya.bind(null, n, r, e), [
      e
    ]),
    r.getSnapshot !== t ||
    i ||
    Z !== null &&
    Z.memoizedState.tag & 1
  ) {
    if (
      n.flags |= 2048,
      Yn(9, va.bind(null, n, r, l, t), void 0, null),
      J === null
    ) throw Error(g(349));
    _t & 30 ||
    ha(n, t, l)
  }
  return l
}
function ha(e, t, n) {
  e.flags |= 16384,
  e = {
    getSnapshot: t,
    value: n
  },
  t = $.updateQueue,
  t === null ? (t = {
    lastEffect: null,
    stores: null
  }, $.updateQueue = t, t.stores = [
    e
  ]) : (n = t.stores, n === null ? t.stores = [
    e
  ] : n.push(e))
}
function va(e, t, n, r) {
  t.value = n,
  t.getSnapshot = r,
  ga(t) &&
  xa(e)
}
function ya(e, t, n) {
  return n(function () {
    ga(t) &&
    xa(e)
  })
}
function ga(e) {
  var t = e.getSnapshot;
  e = e.value;
  try {
    var n = t();
    return !Oe(e, n)
  } catch {
    return !0
  }
}
function xa(e) {
  var t = Ye(e, 1);
  t !== null &&
  Me(t, e, 1, - 1)
}
function No(e) {
  var t = Ie();
  return typeof e == 'function' &&
  (e = e()),
  t.memoizedState = t.baseState = e,
  e = {
    pending: null,
    interleaved: null,
    lanes: 0,
    dispatch: null,
    lastRenderedReducer: Gn,
    lastRenderedState: e
  },
  t.queue = e,
  e = e.dispatch = cf.bind(null, $, e),
  [
    t.memoizedState,
    e
  ]
}
function Yn(e, t, n, r) {
  return e = {
    tag: e,
    create: t,
    destroy: n,
    deps: r,
    next: null
  },
  t = $.updateQueue,
  t === null ? (
    t = {
      lastEffect: null,
      stores: null
    },
    $.updateQueue = t,
    t.lastEffect = e.next = e
  ) : (
    n = t.lastEffect,
    n === null ? t.lastEffect = e.next = e : (r = n.next, n.next = e, e.next = r, t.lastEffect = e)
  ),
  e
}
function wa() {
  return Ee().memoizedState
}
function Pr(e, t, n, r) {
  var l = Ie();
  $.flags |= e,
  l.memoizedState = Yn(1 | t, n, void 0, r === void 0 ? null : r)
}
function al(e, t, n, r) {
  var l = Ee();
  r = r === void 0 ? null : r;
  var i = void 0;
  if (G !== null) {
    var s = G.memoizedState;
    if (i = s.destroy, r !== null && ys(r, s.deps)) {
      l.memoizedState = Yn(t, n, i, r);
      return
    }
  }
  $.flags |= e,
  l.memoizedState = Yn(1 | t, n, i, r)
}
function jo(e, t) {
  return Pr(8390656, 8, e, t)
}
function ws(e, t) {
  return al(2048, 8, e, t)
}
function ka(e, t) {
  return al(4, 2, e, t)
}
function Sa(e, t) {
  return al(4, 4, e, t)
}
function Na(e, t) {
  if (typeof t == 'function') return e = e(),
  t(e),
  function () {
    t(null)
  };
  if (t != null) return e = e(),
  t.current = e,
  function () {
    t.current = null
  }
}
function ja(e, t, n) {
  return n = n != null ? n.concat([e]) : null,
  al(4, 4, Na.bind(null, t, e), n)
}
function ks() {
}
function Ca(e, t) {
  var n = Ee();
  t = t === void 0 ? null : t;
  var r = n.memoizedState;
  return r !== null &&
  t !== null &&
  ys(t, r[1]) ? r[0] : (n.memoizedState = [
    e,
    t
  ], e)
}
function Ea(e, t) {
  var n = Ee();
  t = t === void 0 ? null : t;
  var r = n.memoizedState;
  return r !== null &&
  t !== null &&
  ys(t, r[1]) ? r[0] : (e = e(), n.memoizedState = [
    e,
    t
  ], e)
}
function Pa(e, t, n) {
  return _t & 21 ? (Oe(n, t) || (n = Lu(), $.lanes |= n, Rt |= n, e.baseState = !0), t) : (e.baseState && (e.baseState = !1, de = !0), e.memoizedState = n)
}
function uf(e, t) {
  var n = M;
  M = n !== 0 &&
  4 > n ? n : 4,
  e(!0);
  var r = $l.transition;
  $l.transition = {};
  try {
    e(!1),
    t()
  } finally {
    M = n,
    $l.transition = r
  }
}
function _a() {
  return Ee().memoizedState
}
function af(e, t, n) {
  var r = ct(e);
  if (
    n = {
      lane: r,
      action: n,
      hasEagerState: !1,
      eagerState: null,
      next: null
    },
    Ra(e)
  ) za(t, n);
   else if (n = ca(e, t, n, r), n !== null) {
    var l = oe();
    Me(n, e, r, l),
    Ta(n, t, r)
  }
}
function cf(e, t, n) {
  var r = ct(e),
  l = {
    lane: r,
    action: n,
    hasEagerState: !1,
    eagerState: null,
    next: null
  };
  if (Ra(e)) za(t, l);
   else {
    var i = e.alternate;
    if (
      e.lanes === 0 &&
      (i === null || i.lanes === 0) &&
      (i = t.lastRenderedReducer, i !== null)
    ) try {
      var s = t.lastRenderedState,
      u = i(s, n);
      if (l.hasEagerState = !0, l.eagerState = u, Oe(u, s)) {
        var a = t.interleaved;
        a === null ? (l.next = l, fs(t)) : (l.next = a.next, a.next = l),
        t.interleaved = l;
        return
      }
    } catch {
    } finally {
    }
    n = ca(e, t, l, r),
    n !== null &&
    (l = oe(), Me(n, e, r, l), Ta(n, t, r))
  }
}
function Ra(e) {
  var t = e.alternate;
  return e === $ ||
  t !== null &&
  t === $
}
function za(e, t) {
  Rn = Xr = !0;
  var n = e.pending;
  n === null ? t.next = t : (t.next = n.next, n.next = t),
  e.pending = t
}
function Ta(e, t, n) {
  if (n & 4194240) {
    var r = t.lanes;
    r &= e.pendingLanes,
    n |= r,
    t.lanes = n,
    qi(e, n)
  }
}
var Zr = {
  readContext: Ce,
  useCallback: ne,
  useContext: ne,
  useEffect: ne,
  useImperativeHandle: ne,
  useInsertionEffect: ne,
  useLayoutEffect: ne,
  useMemo: ne,
  useReducer: ne,
  useRef: ne,
  useState: ne,
  useDebugValue: ne,
  useDeferredValue: ne,
  useTransition: ne,
  useMutableSource: ne,
  useSyncExternalStore: ne,
  useId: ne,
  unstable_isNewReconciler: !1
},
df = {
  readContext: Ce,
  useCallback: function (e, t) {
    return Ie().memoizedState = [
      e,
      t === void 0 ? null : t
    ],
    e
  },
  useContext: Ce,
  useEffect: jo,
  useImperativeHandle: function (e, t, n) {
    return n = n != null ? n.concat([e]) : null,
    Pr(4194308, 4, Na.bind(null, t, e), n)
  },
  useLayoutEffect: function (e, t) {
    return Pr(4194308, 4, e, t)
  },
  useInsertionEffect: function (e, t) {
    return Pr(4, 2, e, t)
  },
  useMemo: function (e, t) {
    var n = Ie();
    return t = t === void 0 ? null : t,
    e = e(),
    n.memoizedState = [
      e,
      t
    ],
    e
  },
  useReducer: function (e, t, n) {
    var r = Ie();
    return t = n !== void 0 ? n(t) : t,
    r.memoizedState = r.baseState = t,
    e = {
      pending: null,
      interleaved: null,
      lanes: 0,
      dispatch: null,
      lastRenderedReducer: e,
      lastRenderedState: t
    },
    r.queue = e,
    e = e.dispatch = af.bind(null, $, e),
    [
      r.memoizedState,
      e
    ]
  },
  useRef: function (e) {
    var t = Ie();
    return e = {
      current: e
    },
    t.memoizedState = e
  },
  useState: No,
  useDebugValue: ks,
  useDeferredValue: function (e) {
    return Ie().memoizedState = e
  },
  useTransition: function () {
    var e = No(!1),
    t = e[0];
    return e = uf.bind(null, e[1]),
    Ie().memoizedState = e,
    [
      t,
      e
    ]
  },
  useMutableSource: function () {
  },
  useSyncExternalStore: function (e, t, n) {
    var r = $,
    l = Ie();
    if (U) {
      if (n === void 0) throw Error(g(407));
      n = n()
    } else {
      if (n = t(), J === null) throw Error(g(349));
      _t & 30 ||
      ha(r, t, n)
    }
    l.memoizedState = n;
    var i = {
      value: n,
      getSnapshot: t
    };
    return l.queue = i,
    jo(ya.bind(null, r, i, e), [
      e
    ]),
    r.flags |= 2048,
    Yn(9, va.bind(null, r, i, n, t), void 0, null),
    n
  },
  useId: function () {
    var e = Ie(),
    t = J.identifierPrefix;
    if (U) {
      var n = We,
      r = Be;
      n = (r & ~(1 << 32 - Le(r) - 1)).toString(32) + n,
      t = ':' + t + 'R' + n,
      n = Kn++,
      0 < n &&
      (t += 'H' + n.toString(32)),
      t += ':'
    } else n = of ++,
    t = ':' + t + 'r' + n.toString(32) + ':';
    return e.memoizedState = t
  },
  unstable_isNewReconciler: !1
},
ff = {
  readContext: Ce,
  useCallback: Ca,
  useContext: Ce,
  useEffect: ws,
  useImperativeHandle: ja,
  useInsertionEffect: ka,
  useLayoutEffect: Sa,
  useMemo: Ea,
  useReducer: Hl,
  useRef: wa,
  useState: function () {
    return Hl(Gn)
  },
  useDebugValue: ks,
  useDeferredValue: function (e) {
    var t = Ee();
    return Pa(t, G.memoizedState, e)
  },
  useTransition: function () {
    var e = Hl(Gn) [0],
    t = Ee().memoizedState;
    return [e,
    t]
  },
  useMutableSource: pa,
  useSyncExternalStore: ma,
  useId: _a,
  unstable_isNewReconciler: !1
},
pf = {
  readContext: Ce,
  useCallback: Ca,
  useContext: Ce,
  useEffect: ws,
  useImperativeHandle: ja,
  useInsertionEffect: ka,
  useLayoutEffect: Sa,
  useMemo: Ea,
  useReducer: Vl,
  useRef: wa,
  useState: function () {
    return Vl(Gn)
  },
  useDebugValue: ks,
  useDeferredValue: function (e) {
    var t = Ee();
    return G === null ? t.memoizedState = e : Pa(t, G.memoizedState, e)
  },
  useTransition: function () {
    var e = Vl(Gn) [0],
    t = Ee().memoizedState;
    return [e,
    t]
  },
  useMutableSource: pa,
  useSyncExternalStore: ma,
  useId: _a,
  unstable_isNewReconciler: !1
};
function Re(e, t) {
  if (e && e.defaultProps) {
    t = H({
    }, t),
    e = e.defaultProps;
    for (var n in e) t[n] === void 0 &&
    (t[n] = e[n]);
    return t
  }
  return t
}
function Ni(e, t, n, r) {
  t = e.memoizedState,
  n = n(r, t),
  n = n == null ? t : H({
  }, t, n),
  e.memoizedState = n,
  e.lanes === 0 &&
  (e.updateQueue.baseState = n)
}
var cl = {
  isMounted: function (e) {
    return (e = e._reactInternals) ? Lt(e) === e : !1
  },
  enqueueSetState: function (e, t, n) {
    e = e._reactInternals;
    var r = oe(),
    l = ct(e),
    i = Qe(r, l);
    i.payload = t,
    n != null &&
    (i.callback = n),
    t = ut(e, i, l),
    t !== null &&
    (Me(t, e, l, r), Cr(t, e, l))
  },
  enqueueReplaceState: function (e, t, n) {
    e = e._reactInternals;
    var r = oe(),
    l = ct(e),
    i = Qe(r, l);
    i.tag = 1,
    i.payload = t,
    n != null &&
    (i.callback = n),
    t = ut(e, i, l),
    t !== null &&
    (Me(t, e, l, r), Cr(t, e, l))
  },
  enqueueForceUpdate: function (e, t) {
    e = e._reactInternals;
    var n = oe(),
    r = ct(e),
    l = Qe(n, r);
    l.tag = 2,
    t != null &&
    (l.callback = t),
    t = ut(e, l, r),
    t !== null &&
    (Me(t, e, r, n), Cr(t, e, r))
  }
};
function Co(e, t, n, r, l, i, s) {
  return e = e.stateNode,
  typeof e.shouldComponentUpdate == 'function' ? e.shouldComponentUpdate(r, i, s) : t.prototype &&
  t.prototype.isPureReactComponent ? !$n(n, r) ||
  !$n(l, i) : !0
}
function La(e, t, n) {
  var r = !1,
  l = pt,
  i = t.contextType;
  return typeof i == 'object' &&
  i !== null ? i = Ce(i) : (
    l = pe(t) ? Et : ie.current,
    r = t.contextTypes,
    i = (r = r != null) ? bt(e, l) : pt
  ),
  t = new t(n, i),
  e.memoizedState = t.state !== null &&
  t.state !== void 0 ? t.state : null,
  t.updater = cl,
  e.stateNode = t,
  t._reactInternals = e,
  r &&
  (
    e = e.stateNode,
    e.__reactInternalMemoizedUnmaskedChildContext = l,
    e.__reactInternalMemoizedMaskedChildContext = i
  ),
  t
}
function Eo(e, t, n, r) {
  e = t.state,
  typeof t.componentWillReceiveProps == 'function' &&
  t.componentWillReceiveProps(n, r),
  typeof t.UNSAFE_componentWillReceiveProps == 'function' &&
  t.UNSAFE_componentWillReceiveProps(n, r),
  t.state !== e &&
  cl.enqueueReplaceState(t, t.state, null)
}
function ji(e, t, n, r) {
  var l = e.stateNode;
  l.props = n,
  l.state = e.memoizedState,
  l.refs = {},
  ps(e);
  var i = t.contextType;
  typeof i == 'object' &&
  i !== null ? l.context = Ce(i) : (i = pe(t) ? Et : ie.current, l.context = bt(e, i)),
  l.state = e.memoizedState,
  i = t.getDerivedStateFromProps,
  typeof i == 'function' &&
  (Ni(e, t, i, n), l.state = e.memoizedState),
  typeof t.getDerivedStateFromProps == 'function' ||
  typeof l.getSnapshotBeforeUpdate == 'function' ||
  typeof l.UNSAFE_componentWillMount != 'function' &&
  typeof l.componentWillMount != 'function' ||
  (
    t = l.state,
    typeof l.componentWillMount == 'function' &&
    l.componentWillMount(),
    typeof l.UNSAFE_componentWillMount == 'function' &&
    l.UNSAFE_componentWillMount(),
    t !== l.state &&
    cl.enqueueReplaceState(l, l.state, null),
    Gr(e, n, l, r),
    l.state = e.memoizedState
  ),
  typeof l.componentDidMount == 'function' &&
  (e.flags |= 4194308)
}
function rn(e, t) {
  try {
    var n = '',
    r = t;
    do n += $c(r),
    r = r.return;
    while (r);
    var l = n
  } catch (i) {
    l = `
Error generating stack: 
    ` + i.message + `

    ` + i.stack
  }
  return {
    value: e,
    source: t,
    stack: l,
    digest: null
  }
}
function Bl(e, t, n) {
  return {
    value: e,
    source: null,
    stack: n ?? null,
    digest: t ?? null
  }
}
function Ci(e, t) {
  try {
    console.error(t.value)
  } catch (n) {
    setTimeout(function () {
      throw n
    })
  }
}
var mf = typeof WeakMap == 'function' ? WeakMap : Map;
function Ma(e, t, n) {
  n = Qe( - 1, n),
  n.tag = 3,
  n.payload = {
    element: null
  };
  var r = t.value;
  return n.callback = function () {
    qr ||
    (qr = !0, Di = r),
    Ci(e, t)
  },
  n
}
function Oa(e, t, n) {
  n = Qe( - 1, n),
  n.tag = 3;
  var r = e.type.getDerivedStateFromError;
  if (typeof r == 'function') {
    var l = t.value;
    n.payload = function () {
      return r(l)
    },
    n.callback = function () {
      Ci(e, t)
    }
  }
  var i = e.stateNode;
  return i !== null &&
  typeof i.componentDidCatch == 'function' &&
  (
    n.callback = function () {
      Ci(e, t),
      typeof r != 'function' &&
      (at === null ? at = new Set([this]) : at.add(this));
      var s = t.stack;
      this.componentDidCatch(t.value, {
        componentStack: s !== null ? s : ''
      })
    }
  ),
  n
}
function Po(e, t, n) {
  var r = e.pingCache;
  if (r === null) {
    r = e.pingCache = new mf;
    var l = new Set;
    r.set(t, l)
  } else l = r.get(t),
  l === void 0 &&
  (l = new Set, r.set(t, l));
  l.has(n) ||
  (l.add(n), e = _f.bind(null, e, t, n), t.then(e, e))
}
function _o(e) {
  do {
    var t;
    if (
      (t = e.tag === 13) &&
      (t = e.memoizedState, t = t !== null ? t.dehydrated !== null : !0),
      t
    ) return e;
    e = e.return
  } while (e !== null);
  return null
}
function Ro(e, t, n, r, l) {
  return e.mode & 1 ? (e.flags |= 65536, e.lanes = l, e) : (
    e === t ? e.flags |= 65536 : (
      e.flags |= 128,
      n.flags |= 131072,
      n.flags &= - 52805,
      n.tag === 1 &&
      (n.alternate === null ? n.tag = 17 : (t = Qe( - 1, 1), t.tag = 2, ut(n, t, 1))),
      n.lanes |= 1
    ),
    e
  )
}
var hf = Ze.ReactCurrentOwner,
de = !1;
function se(e, t, n, r) {
  t.child = e === null ? aa(t, null, n, r) : tn(t, e.child, n, r)
}
function zo(e, t, n, r, l) {
  n = n.render;
  var i = t.ref;
  return Zt(t, l),
  r = gs(e, t, n, r, i, l),
  n = xs(),
  e !== null &&
  !de ? (
    t.updateQueue = e.updateQueue,
    t.flags &= - 2053,
    e.lanes &= ~l,
    Xe(e, t, l)
  ) : (U && n && ss(t), t.flags |= 1, se(e, t, r, l), t.child)
}
function To(e, t, n, r, l) {
  if (e === null) {
    var i = n.type;
    return typeof i == 'function' &&
    !Rs(i) &&
    i.defaultProps === void 0 &&
    n.compare === null &&
    n.defaultProps === void 0 ? (t.tag = 15, t.type = i, Da(e, t, i, r, l)) : (
      e = Tr(n.type, null, r, t, t.mode, l),
      e.ref = t.ref,
      e.return = t,
      t.child = e
    )
  }
  if (i = e.child, !(e.lanes & l)) {
    var s = i.memoizedProps;
    if (n = n.compare, n = n !== null ? n : $n, n(s, r) && e.ref === t.ref) return Xe(e, t, l)
  }
  return t.flags |= 1,
  e = dt(i, r),
  e.ref = t.ref,
  e.return = t,
  t.child = e
}
function Da(e, t, n, r, l) {
  if (e !== null) {
    var i = e.memoizedProps;
    if ($n(i, r) && e.ref === t.ref) if (de = !1, t.pendingProps = r = i, (e.lanes & l) !== 0) e.flags & 131072 &&
    (de = !0);
     else return t.lanes = e.lanes,
    Xe(e, t, l)
  }
  return Ei(e, t, n, r, l)
}
function Ia(e, t, n) {
  var r = t.pendingProps,
  l = r.children,
  i = e !== null ? e.memoizedState : null;
  if (r.mode === 'hidden') if (!(t.mode & 1)) t.memoizedState = {
    baseLanes: 0,
    cachePool: null,
    transitions: null
  },
  O(Qt, he),
  he |= n;
   else {
    if (!(n & 1073741824)) return e = i !== null ? i.baseLanes | n : n,
    t.lanes = t.childLanes = 1073741824,
    t.memoizedState = {
      baseLanes: e,
      cachePool: null,
      transitions: null
    },
    t.updateQueue = null,
    O(Qt, he),
    he |= e,
    null;
    t.memoizedState = {
      baseLanes: 0,
      cachePool: null,
      transitions: null
    },
    r = i !== null ? i.baseLanes : n,
    O(Qt, he),
    he |= r
  } else i !== null ? (r = i.baseLanes | n, t.memoizedState = null) : r = n,
  O(Qt, he),
  he |= r;
  return se(e, t, l, n),
  t.child
}
function Fa(e, t) {
  var n = t.ref;
  (e === null && n !== null || e !== null && e.ref !== n) &&
  (t.flags |= 512, t.flags |= 2097152)
}
function Ei(e, t, n, r, l) {
  var i = pe(n) ? Et : ie.current;
  return i = bt(t, i),
  Zt(t, l),
  n = gs(e, t, n, r, i, l),
  r = xs(),
  e !== null &&
  !de ? (
    t.updateQueue = e.updateQueue,
    t.flags &= - 2053,
    e.lanes &= ~l,
    Xe(e, t, l)
  ) : (U && r && ss(t), t.flags |= 1, se(e, t, n, l), t.child)
}
function Lo(e, t, n, r, l) {
  if (pe(n)) {
    var i = !0;
    Vr(t)
  } else i = !1;
  if (Zt(t, l), t.stateNode === null) _r(e, t),
  La(t, n, r),
  ji(t, n, r, l),
  r = !0;
   else if (e === null) {
    var s = t.stateNode,
    u = t.memoizedProps;
    s.props = u;
    var a = s.context,
    d = n.contextType;
    typeof d == 'object' &&
    d !== null ? d = Ce(d) : (d = pe(n) ? Et : ie.current, d = bt(t, d));
    var v = n.getDerivedStateFromProps,
    h = typeof v == 'function' ||
    typeof s.getSnapshotBeforeUpdate == 'function';
    h ||
    typeof s.UNSAFE_componentWillReceiveProps != 'function' &&
    typeof s.componentWillReceiveProps != 'function' ||
    (u !== r || a !== d) &&
    Eo(t, s, r, d),
    be = !1;
    var m = t.memoizedState;
    s.state = m,
    Gr(t, r, s, l),
    a = t.memoizedState,
    u !== r ||
    m !== a ||
    fe.current ||
    be ? (
      typeof v == 'function' &&
      (Ni(t, n, v, r), a = t.memoizedState),
      (u = be || Co(t, n, u, r, m, a, d)) ? (
        h ||
        typeof s.UNSAFE_componentWillMount != 'function' &&
        typeof s.componentWillMount != 'function' ||
        (
          typeof s.componentWillMount == 'function' &&
          s.componentWillMount(),
          typeof s.UNSAFE_componentWillMount == 'function' &&
          s.UNSAFE_componentWillMount()
        ),
        typeof s.componentDidMount == 'function' &&
        (t.flags |= 4194308)
      ) : (
        typeof s.componentDidMount == 'function' &&
        (t.flags |= 4194308),
        t.memoizedProps = r,
        t.memoizedState = a
      ),
      s.props = r,
      s.state = a,
      s.context = d,
      r = u
    ) : (
      typeof s.componentDidMount == 'function' &&
      (t.flags |= 4194308),
      r = !1
    )
  } else {
    s = t.stateNode,
    da(e, t),
    u = t.memoizedProps,
    d = t.type === t.elementType ? u : Re(t.type, u),
    s.props = d,
    h = t.pendingProps,
    m = s.context,
    a = n.contextType,
    typeof a == 'object' &&
    a !== null ? a = Ce(a) : (a = pe(n) ? Et : ie.current, a = bt(t, a));
    var x = n.getDerivedStateFromProps;
    (
      v = typeof x == 'function' ||
      typeof s.getSnapshotBeforeUpdate == 'function'
    ) ||
    typeof s.UNSAFE_componentWillReceiveProps != 'function' &&
    typeof s.componentWillReceiveProps != 'function' ||
    (u !== h || m !== a) &&
    Eo(t, s, r, a),
    be = !1,
    m = t.memoizedState,
    s.state = m,
    Gr(t, r, s, l);
    var w = t.memoizedState;
    u !== h ||
    m !== w ||
    fe.current ||
    be ? (
      typeof x == 'function' &&
      (Ni(t, n, x, r), w = t.memoizedState),
      (d = be || Co(t, n, d, r, m, w, a) || !1) ? (
        v ||
        typeof s.UNSAFE_componentWillUpdate != 'function' &&
        typeof s.componentWillUpdate != 'function' ||
        (
          typeof s.componentWillUpdate == 'function' &&
          s.componentWillUpdate(r, w, a),
          typeof s.UNSAFE_componentWillUpdate == 'function' &&
          s.UNSAFE_componentWillUpdate(r, w, a)
        ),
        typeof s.componentDidUpdate == 'function' &&
        (t.flags |= 4),
        typeof s.getSnapshotBeforeUpdate == 'function' &&
        (t.flags |= 1024)
      ) : (
        typeof s.componentDidUpdate != 'function' ||
        u === e.memoizedProps &&
        m === e.memoizedState ||
        (t.flags |= 4),
        typeof s.getSnapshotBeforeUpdate != 'function' ||
        u === e.memoizedProps &&
        m === e.memoizedState ||
        (t.flags |= 1024),
        t.memoizedProps = r,
        t.memoizedState = w
      ),
      s.props = r,
      s.state = w,
      s.context = a,
      r = d
    ) : (
      typeof s.componentDidUpdate != 'function' ||
      u === e.memoizedProps &&
      m === e.memoizedState ||
      (t.flags |= 4),
      typeof s.getSnapshotBeforeUpdate != 'function' ||
      u === e.memoizedProps &&
      m === e.memoizedState ||
      (t.flags |= 1024),
      r = !1
    )
  }
  return Pi(e, t, n, r, i, l)
}
function Pi(e, t, n, r, l, i) {
  Fa(e, t);
  var s = (t.flags & 128) !== 0;
  if (!r && !s) return l &&
  yo(t, n, !1),
  Xe(e, t, i);
  r = t.stateNode,
  hf.current = t;
  var u = s &&
  typeof n.getDerivedStateFromError != 'function' ? null : r.render();
  return t.flags |= 1,
  e !== null &&
  s ? (t.child = tn(t, e.child, null, i), t.child = tn(t, null, u, i)) : se(e, t, u, i),
  t.memoizedState = r.state,
  l &&
  yo(t, n, !0),
  t.child
}
function Ua(e) {
  var t = e.stateNode;
  t.pendingContext ? vo(e, t.pendingContext, t.pendingContext !== t.context) : t.context &&
  vo(e, t.context, !1),
  ms(e, t.containerInfo)
}
function Mo(e, t, n, r, l) {
  return en(),
  us(l),
  t.flags |= 256,
  se(e, t, n, r),
  t.child
}
var _i = {
  dehydrated: null,
  treeContext: null,
  retryLane: 0
};
function Ri(e) {
  return {
    baseLanes: e,
    cachePool: null,
    transitions: null
  }
}
function Aa(e, t, n) {
  var r = t.pendingProps,
  l = A.current,
  i = !1,
  s = (t.flags & 128) !== 0,
  u;
  if (
    (u = s) ||
    (u = e !== null && e.memoizedState === null ? !1 : (l & 2) !== 0),
    u ? (i = !0, t.flags &= - 129) : (e === null || e.memoizedState !== null) &&
    (l |= 1),
    O(A, l & 1),
    e === null
  ) return ki(t),
  e = t.memoizedState,
  e !== null &&
  (e = e.dehydrated, e !== null) ? (
    t.mode & 1 ? e.data === '$!' ? t.lanes = 8 : t.lanes = 1073741824 : t.lanes = 1,
    null
  ) : (
    s = r.children,
    e = r.fallback,
    i ? (
      r = t.mode,
      i = t.child,
      s = {
        mode: 'hidden',
        children: s
      },
      !(r & 1) &&
      i !== null ? (i.childLanes = 0, i.pendingProps = s) : i = pl(s, r, 0, null),
      e = Ct(e, r, n, null),
      i.return = t,
      e.return = t,
      i.sibling = e,
      t.child = i,
      t.child.memoizedState = Ri(n),
      t.memoizedState = _i,
      e
    ) : Ss(t, s)
  );
  if (l = e.memoizedState, l !== null && (u = l.dehydrated, u !== null)) return vf(e, t, s, r, u, l, n);
  if (i) {
    i = r.fallback,
    s = t.mode,
    l = e.child,
    u = l.sibling;
    var a = {
      mode: 'hidden',
      children: r.children
    };
    return !(s & 1) &&
    t.child !== l ? (r = t.child, r.childLanes = 0, r.pendingProps = a, t.deletions = null) : (r = dt(l, a), r.subtreeFlags = l.subtreeFlags & 14680064),
    u !== null ? i = dt(u, i) : (i = Ct(i, s, n, null), i.flags |= 2),
    i.return = t,
    r.return = t,
    r.sibling = i,
    t.child = r,
    r = i,
    i = t.child,
    s = e.child.memoizedState,
    s = s === null ? Ri(n) : {
      baseLanes: s.baseLanes | n,
      cachePool: null,
      transitions: s.transitions
    },
    i.memoizedState = s,
    i.childLanes = e.childLanes & ~n,
    t.memoizedState = _i,
    r
  }
  return i = e.child,
  e = i.sibling,
  r = dt(i, {
    mode: 'visible',
    children: r.children
  }),
  !(t.mode & 1) &&
  (r.lanes = n),
  r.return = t,
  r.sibling = null,
  e !== null &&
  (
    n = t.deletions,
    n === null ? (t.deletions = [
      e
    ], t.flags |= 16) : n.push(e)
  ),
  t.child = r,
  t.memoizedState = null,
  r
}
function Ss(e, t) {
  return t = pl({
    mode: 'visible',
    children: t
  }, e.mode, 0, null),
  t.return = e,
  e.child = t
}
function vr(e, t, n, r) {
  return r !== null &&
  us(r),
  tn(t, e.child, null, n),
  e = Ss(t, t.pendingProps.children),
  e.flags |= 2,
  t.memoizedState = null,
  e
}
function vf(e, t, n, r, l, i, s) {
  if (n) return t.flags & 256 ? (t.flags &= - 257, r = Bl(Error(g(422))), vr(e, t, s, r)) : t.memoizedState !== null ? (t.child = e.child, t.flags |= 128, null) : (
    i = r.fallback,
    l = t.mode,
    r = pl({
      mode: 'visible',
      children: r.children
    }, l, 0, null),
    i = Ct(i, l, s, null),
    i.flags |= 2,
    r.return = t,
    i.return = t,
    r.sibling = i,
    t.child = r,
    t.mode & 1 &&
    tn(t, e.child, null, s),
    t.child.memoizedState = Ri(s),
    t.memoizedState = _i,
    i
  );
  if (!(t.mode & 1)) return vr(e, t, s, null);
  if (l.data === '$!') {
    if (r = l.nextSibling && l.nextSibling.dataset, r) var u = r.dgst;
    return r = u,
    i = Error(g(419)),
    r = Bl(i, r, void 0),
    vr(e, t, s, r)
  }
  if (u = (s & e.childLanes) !== 0, de || u) {
    if (r = J, r !== null) {
      switch (s & - s) {
        case 4:
          l = 2;
          break;
        case 16:
          l = 8;
          break;
        case 64:
        case 128:
        case 256:
        case 512:
        case 1024:
        case 2048:
        case 4096:
        case 8192:
        case 16384:
        case 32768:
        case 65536:
        case 131072:
        case 262144:
        case 524288:
        case 1048576:
        case 2097152:
        case 4194304:
        case 8388608:
        case 16777216:
        case 33554432:
        case 67108864:
          l = 32;
          break;
        case 536870912:
          l = 268435456;
          break;
        default:
          l = 0
      }
      l = l & (r.suspendedLanes | s) ? 0 : l,
      l !== 0 &&
      l !== i.retryLane &&
      (i.retryLane = l, Ye(e, l), Me(r, e, l, - 1))
    }
    return _s(),
    r = Bl(Error(g(421))),
    vr(e, t, s, r)
  }
  return l.data === '$?' ? (
    t.flags |= 128,
    t.child = e.child,
    t = Rf.bind(null, e),
    l._reactRetry = t,
    null
  ) : (
    e = i.treeContext,
    ve = ot(l.nextSibling),
    ye = t,
    U = !0,
    Te = null,
    e !== null &&
    (
      ke[Se++] = Be,
      ke[Se++] = We,
      ke[Se++] = Pt,
      Be = e.id,
      We = e.overflow,
      Pt = t
    ),
    t = Ss(t, r.children),
    t.flags |= 4096,
    t
  )
}
function Oo(e, t, n) {
  e.lanes |= t;
  var r = e.alternate;
  r !== null &&
  (r.lanes |= t),
  Si(e.return, t, n)
}
function Wl(e, t, n, r, l) {
  var i = e.memoizedState;
  i === null ? e.memoizedState = {
    isBackwards: t,
    rendering: null,
    renderingStartTime: 0,
    last: r,
    tail: n,
    tailMode: l
  }
   : (
    i.isBackwards = t,
    i.rendering = null,
    i.renderingStartTime = 0,
    i.last = r,
    i.tail = n,
    i.tailMode = l
  )
}
function $a(e, t, n) {
  var r = t.pendingProps,
  l = r.revealOrder,
  i = r.tail;
  if (se(e, t, r.children, n), r = A.current, r & 2) r = r & 1 | 2,
  t.flags |= 128;
   else {
    if (e !== null && e.flags & 128) e: for (e = t.child; e !== null; ) {
      if (e.tag === 13) e.memoizedState !== null &&
      Oo(e, n, t);
       else if (e.tag === 19) Oo(e, n, t);
       else if (e.child !== null) {
        e.child.return = e,
        e = e.child;
        continue
      }
      if (e === t) break e;
      for (; e.sibling === null; ) {
        if (e.return === null || e.return === t) break e;
        e = e.return
      }
      e.sibling.return = e.return,
      e = e.sibling
    }
    r &= 1
  }
  if (O(A, r), !(t.mode & 1)) t.memoizedState = null;
   else switch (l) {
    case 'forwards':
      for (n = t.child, l = null; n !== null; ) e = n.alternate,
      e !== null &&
      Yr(e) === null &&
      (l = n),
      n = n.sibling;
      n = l,
      n === null ? (l = t.child, t.child = null) : (l = n.sibling, n.sibling = null),
      Wl(t, !1, l, n, i);
      break;
    case 'backwards':
      for (n = null, l = t.child, t.child = null; l !== null; ) {
        if (e = l.alternate, e !== null && Yr(e) === null) {
          t.child = l;
          break
        }
        e = l.sibling,
        l.sibling = n,
        n = l,
        l = e
      }
      Wl(t, !0, n, null, i);
      break;
    case 'together':
      Wl(t, !1, null, null, void 0);
      break;
    default:
      t.memoizedState = null
  }
  return t.child
}
function _r(e, t) {
  !(t.mode & 1) &&
  e !== null &&
  (e.alternate = null, t.alternate = null, t.flags |= 2)
}
function Xe(e, t, n) {
  if (
    e !== null &&
    (t.dependencies = e.dependencies),
    Rt |= t.lanes,
    !(n & t.childLanes)
  ) return null;
  if (e !== null && t.child !== e.child) throw Error(g(153));
  if (t.child !== null) {
    for (
      e = t.child,
      n = dt(e, e.pendingProps),
      t.child = n,
      n.return = t;
      e.sibling !== null;
    ) e = e.sibling,
    n = n.sibling = dt(e, e.pendingProps),
    n.return = t;
    n.sibling = null
  }
  return t.child
}
function yf(e, t, n) {
  switch (t.tag) {
    case 3:
      Ua(t),
      en();
      break;
    case 5:
      fa(t);
      break;
    case 1:
      pe(t.type) &&
      Vr(t);
      break;
    case 4:
      ms(t, t.stateNode.containerInfo);
      break;
    case 10:
      var r = t.type._context,
      l = t.memoizedProps.value;
      O(Qr, r._currentValue),
      r._currentValue = l;
      break;
    case 13:
      if (r = t.memoizedState, r !== null) return r.dehydrated !== null ? (O(A, A.current & 1), t.flags |= 128, null) : n & t.child.childLanes ? Aa(e, t, n) : (O(A, A.current & 1), e = Xe(e, t, n), e !== null ? e.sibling : null);
      O(A, A.current & 1);
      break;
    case 19:
      if (r = (n & t.childLanes) !== 0, e.flags & 128) {
        if (r) return $a(e, t, n);
        t.flags |= 128
      }
      if (
        l = t.memoizedState,
        l !== null &&
        (l.rendering = null, l.tail = null, l.lastEffect = null),
        O(A, A.current),
        r
      ) break;
      return null;
    case 22:
    case 23:
      return t.lanes = 0,
      Ia(e, t, n)
  }
  return Xe(e, t, n)
}
var Ha,
zi,
Va,
Ba;
Ha = function (e, t) {
  for (var n = t.child; n !== null; ) {
    if (n.tag === 5 || n.tag === 6) e.appendChild(n.stateNode);
     else if (n.tag !== 4 && n.child !== null) {
      n.child.return = n,
      n = n.child;
      continue
    }
    if (n === t) break;
    for (; n.sibling === null; ) {
      if (n.return === null || n.return === t) return;
      n = n.return
    }
    n.sibling.return = n.return,
    n = n.sibling
  }
};
zi = function () {
};
Va = function (e, t, n, r) {
  var l = e.memoizedProps;
  if (l !== r) {
    e = t.stateNode,
    Nt($e.current);
    var i = null;
    switch (n) {
      case 'input':
        l = ql(e, l),
        r = ql(e, r),
        i = [];
        break;
      case 'select':
        l = H({
        }, l, {
          value: void 0
        }),
        r = H({
        }, r, {
          value: void 0
        }),
        i = [];
        break;
      case 'textarea':
        l = ti(e, l),
        r = ti(e, r),
        i = [];
        break;
      default:
        typeof l.onClick != 'function' &&
        typeof r.onClick == 'function' &&
        (e.onclick = $r)
    }
    ri(n, r);
    var s;
    n = null;
    for (d in l) if (!r.hasOwnProperty(d) && l.hasOwnProperty(d) && l[d] != null) if (d === 'style') {
      var u = l[d];
      for (s in u) u.hasOwnProperty(s) &&
      (n || (n = {}), n[s] = '')
    } else d !== 'dangerouslySetInnerHTML' &&
    d !== 'children' &&
    d !== 'suppressContentEditableWarning' &&
    d !== 'suppressHydrationWarning' &&
    d !== 'autoFocus' &&
    (Mn.hasOwnProperty(d) ? i ||
    (i = []) : (i = i || []).push(d, null));
    for (d in r) {
      var a = r[d];
      if (
        u = l != null ? l[d] : void 0,
        r.hasOwnProperty(d) &&
        a !== u &&
        (a != null || u != null)
      ) if (d === 'style') if (u) {
        for (s in u) !u.hasOwnProperty(s) ||
        a &&
        a.hasOwnProperty(s) ||
        (n || (n = {}), n[s] = '');
        for (s in a) a.hasOwnProperty(s) &&
        u[s] !== a[s] &&
        (n || (n = {}), n[s] = a[s])
      } else n ||
      (i || (i = []), i.push(d, n)),
      n = a;
       else d === 'dangerouslySetInnerHTML' ? (
        a = a ? a.__html : void 0,
        u = u ? u.__html : void 0,
        a != null &&
        u !== a &&
        (i = i || []).push(d, a)
      ) : d === 'children' ? typeof a != 'string' &&
      typeof a != 'number' ||
      (i = i || []).push(d, '' + a) : d !== 'suppressContentEditableWarning' &&
      d !== 'suppressHydrationWarning' &&
      (
        Mn.hasOwnProperty(d) ? (a != null && d === 'onScroll' && D('scroll', e), i || u === a || (i = [])) : (i = i || []).push(d, a)
      )
    }
    n &&
    (i = i || []).push('style', n);
    var d = i;
    (t.updateQueue = d) &&
    (t.flags |= 4)
  }
};
Ba = function (e, t, n, r) {
  n !== r &&
  (t.flags |= 4)
};
function yn(e, t) {
  if (!U) switch (e.tailMode) {
    case 'hidden':
      t = e.tail;
      for (var n = null; t !== null; ) t.alternate !== null &&
      (n = t),
      t = t.sibling;
      n === null ? e.tail = null : n.sibling = null;
      break;
    case 'collapsed':
      n = e.tail;
      for (var r = null; n !== null; ) n.alternate !== null &&
      (r = n),
      n = n.sibling;
      r === null ? t ||
      e.tail === null ? e.tail = null : e.tail.sibling = null : r.sibling = null
  }
}
function re(e) {
  var t = e.alternate !== null &&
  e.alternate.child === e.child,
  n = 0,
  r = 0;
  if (t) for (var l = e.child; l !== null; ) n |= l.lanes | l.childLanes,
  r |= l.subtreeFlags & 14680064,
  r |= l.flags & 14680064,
  l.return = e,
  l = l.sibling;
   else for (l = e.child; l !== null; ) n |= l.lanes | l.childLanes,
  r |= l.subtreeFlags,
  r |= l.flags,
  l.return = e,
  l = l.sibling;
  return e.subtreeFlags |= r,
  e.childLanes = n,
  t
}
function gf(e, t, n) {
  var r = t.pendingProps;
  switch (os(t), t.tag) {
    case 2:
    case 16:
    case 15:
    case 0:
    case 11:
    case 7:
    case 8:
    case 12:
    case 9:
    case 14:
      return re(t),
      null;
    case 1:
      return pe(t.type) &&
      Hr(),
      re(t),
      null;
    case 3:
      return r = t.stateNode,
      nn(),
      I(fe),
      I(ie),
      vs(),
      r.pendingContext &&
      (r.context = r.pendingContext, r.pendingContext = null),
      (e === null || e.child === null) &&
      (
        mr(t) ? t.flags |= 4 : e === null ||
        e.memoizedState.isDehydrated &&
        !(t.flags & 256) ||
        (t.flags |= 1024, Te !== null && (Ui(Te), Te = null))
      ),
      zi(e, t),
      re(t),
      null;
    case 5:
      hs(t);
      var l = Nt(Qn.current);
      if (n = t.type, e !== null && t.stateNode != null) Va(e, t, n, r, l),
      e.ref !== t.ref &&
      (t.flags |= 512, t.flags |= 2097152);
       else {
        if (!r) {
          if (t.stateNode === null) throw Error(g(166));
          return re(t),
          null
        }
        if (e = Nt($e.current), mr(t)) {
          r = t.stateNode,
          n = t.type;
          var i = t.memoizedProps;
          switch (r[Fe] = t, r[Bn] = i, e = (t.mode & 1) !== 0, n) {
            case 'dialog':
              D('cancel', r),
              D('close', r);
              break;
            case 'iframe':
            case 'object':
            case 'embed':
              D('load', r);
              break;
            case 'video':
            case 'audio':
              for (l = 0; l < Sn.length; l++) D(Sn[l], r);
              break;
            case 'source':
              D('error', r);
              break;
            case 'img':
            case 'image':
            case 'link':
              D('error', r),
              D('load', r);
              break;
            case 'details':
              D('toggle', r);
              break;
            case 'input':
              Vs(r, i),
              D('invalid', r);
              break;
            case 'select':
              r._wrapperState = {
                wasMultiple: !!i.multiple
              },
              D('invalid', r);
              break;
            case 'textarea':
              Ws(r, i),
              D('invalid', r)
          }
          ri(n, i),
          l = null;
          for (var s in i) if (i.hasOwnProperty(s)) {
            var u = i[s];
            s === 'children' ? typeof u == 'string' ? r.textContent !== u &&
            (
              i.suppressHydrationWarning !== !0 &&
              pr(r.textContent, u, e),
              l = [
                'children',
                u
              ]
            ) : typeof u == 'number' &&
            r.textContent !== '' + u &&
            (
              i.suppressHydrationWarning !== !0 &&
              pr(r.textContent, u, e),
              l = [
                'children',
                '' + u
              ]
            ) : Mn.hasOwnProperty(s) &&
            u != null &&
            s === 'onScroll' &&
            D('scroll', r)
          }
          switch (n) {
            case 'input':
              ir(r),
              Bs(r, i, !0);
              break;
            case 'textarea':
              ir(r),
              Qs(r);
              break;
            case 'select':
            case 'option':
              break;
            default:
              typeof i.onClick == 'function' &&
              (r.onclick = $r)
          }
          r = l,
          t.updateQueue = r,
          r !== null &&
          (t.flags |= 4)
        } else {
          s = l.nodeType === 9 ? l : l.ownerDocument,
          e === 'http://www.w3.org/1999/xhtml' &&
          (e = yu(n)),
          e === 'http://www.w3.org/1999/xhtml' ? n === 'script' ? (
            e = s.createElement('div'),
            e.innerHTML = '<script></script>',
            e = e.removeChild(e.firstChild)
          ) : typeof r.is == 'string' ? e = s.createElement(n, {
            is: r.is
          }) : (
            e = s.createElement(n),
            n === 'select' &&
            (s = e, r.multiple ? s.multiple = !0 : r.size && (s.size = r.size))
          ) : e = s.createElementNS(e, n),
          e[Fe] = t,
          e[Bn] = r,
          Ha(e, t, !1, !1),
          t.stateNode = e;
          e: {
            switch (s = li(n, r), n) {
              case 'dialog':
                D('cancel', e),
                D('close', e),
                l = r;
                break;
              case 'iframe':
              case 'object':
              case 'embed':
                D('load', e),
                l = r;
                break;
              case 'video':
              case 'audio':
                for (l = 0; l < Sn.length; l++) D(Sn[l], e);
                l = r;
                break;
              case 'source':
                D('error', e),
                l = r;
                break;
              case 'img':
              case 'image':
              case 'link':
                D('error', e),
                D('load', e),
                l = r;
                break;
              case 'details':
                D('toggle', e),
                l = r;
                break;
              case 'input':
                Vs(e, r),
                l = ql(e, r),
                D('invalid', e);
                break;
              case 'option':
                l = r;
                break;
              case 'select':
                e._wrapperState = {
                  wasMultiple: !!r.multiple
                },
                l = H({
                }, r, {
                  value: void 0
                }),
                D('invalid', e);
                break;
              case 'textarea':
                Ws(e, r),
                l = ti(e, r),
                D('invalid', e);
                break;
              default:
                l = r
            }
            ri(n, l),
            u = l;
            for (i in u) if (u.hasOwnProperty(i)) {
              var a = u[i];
              i === 'style' ? wu(e, a) : i === 'dangerouslySetInnerHTML' ? (a = a ? a.__html : void 0, a != null && gu(e, a)) : i === 'children' ? typeof a == 'string' ? (n !== 'textarea' || a !== '') &&
              On(e, a) : typeof a == 'number' &&
              On(e, '' + a) : i !== 'suppressContentEditableWarning' &&
              i !== 'suppressHydrationWarning' &&
              i !== 'autoFocus' &&
              (
                Mn.hasOwnProperty(i) ? a != null &&
                i === 'onScroll' &&
                D('scroll', e) : a != null &&
                Ki(e, i, a, s)
              )
            }
            switch (n) {
              case 'input':
                ir(e),
                Bs(e, r, !1);
                break;
              case 'textarea':
                ir(e),
                Qs(e);
                break;
              case 'option':
                r.value != null &&
                e.setAttribute('value', '' + ft(r.value));
                break;
              case 'select':
                e.multiple = !!r.multiple,
                i = r.value,
                i != null ? Kt(e, !!r.multiple, i, !1) : r.defaultValue != null &&
                Kt(e, !!r.multiple, r.defaultValue, !0);
                break;
              default:
                typeof l.onClick == 'function' &&
                (e.onclick = $r)
            }
            switch (n) {
              case 'button':
              case 'input':
              case 'select':
              case 'textarea':
                r = !!r.autoFocus;
                break e;
              case 'img':
                r = !0;
                break e;
              default:
                r = !1
            }
          }
          r &&
          (t.flags |= 4)
        }
        t.ref !== null &&
        (t.flags |= 512, t.flags |= 2097152)
      }
      return re(t),
      null;
    case 6:
      if (e && t.stateNode != null) Ba(e, t, e.memoizedProps, r);
       else {
        if (typeof r != 'string' && t.stateNode === null) throw Error(g(166));
        if (n = Nt(Qn.current), Nt($e.current), mr(t)) {
          if (
            r = t.stateNode,
            n = t.memoizedProps,
            r[Fe] = t,
            (i = r.nodeValue !== n) &&
            (e = ye, e !== null)
          ) switch (e.tag) {
            case 3:
              pr(r.nodeValue, n, (e.mode & 1) !== 0);
              break;
            case 5:
              e.memoizedProps.suppressHydrationWarning !== !0 &&
              pr(r.nodeValue, n, (e.mode & 1) !== 0)
          }
          i &&
          (t.flags |= 4)
        } else r = (n.nodeType === 9 ? n : n.ownerDocument).createTextNode(r),
        r[Fe] = t,
        t.stateNode = r
      }
      return re(t),
      null;
    case 13:
      if (
        I(A),
        r = t.memoizedState,
        e === null ||
        e.memoizedState !== null &&
        e.memoizedState.dehydrated !== null
      ) {
        if (U && ve !== null && t.mode & 1 && !(t.flags & 128)) oa(),
        en(),
        t.flags |= 98560,
        i = !1;
         else if (i = mr(t), r !== null && r.dehydrated !== null) {
          if (e === null) {
            if (!i) throw Error(g(318));
            if (i = t.memoizedState, i = i !== null ? i.dehydrated : null, !i) throw Error(g(317));
            i[Fe] = t
          } else en(),
          !(t.flags & 128) &&
          (t.memoizedState = null),
          t.flags |= 4;
          re(t),
          i = !1
        } else Te !== null &&
        (Ui(Te), Te = null),
        i = !0;
        if (!i) return t.flags & 65536 ? t : null
      }
      return t.flags & 128 ? (t.lanes = n, t) : (
        r = r !== null,
        r !== (e !== null && e.memoizedState !== null) &&
        r &&
        (
          t.child.flags |= 8192,
          t.mode & 1 &&
          (e === null || A.current & 1 ? Y === 0 &&
          (Y = 3) : _s())
        ),
        t.updateQueue !== null &&
        (t.flags |= 4),
        re(t),
        null
      );
    case 4:
      return nn(),
      zi(e, t),
      e === null &&
      Hn(t.stateNode.containerInfo),
      re(t),
      null;
    case 10:
      return ds(t.type._context),
      re(t),
      null;
    case 17:
      return pe(t.type) &&
      Hr(),
      re(t),
      null;
    case 19:
      if (I(A), i = t.memoizedState, i === null) return re(t),
      null;
      if (r = (t.flags & 128) !== 0, s = i.rendering, s === null) if (r) yn(i, !1);
       else {
        if (Y !== 0 || e !== null && e.flags & 128) for (e = t.child; e !== null; ) {
          if (s = Yr(e), s !== null) {
            for (
              t.flags |= 128,
              yn(i, !1),
              r = s.updateQueue,
              r !== null &&
              (t.updateQueue = r, t.flags |= 4),
              t.subtreeFlags = 0,
              r = n,
              n = t.child;
              n !== null;
            ) i = n,
            e = r,
            i.flags &= 14680066,
            s = i.alternate,
            s === null ? (
              i.childLanes = 0,
              i.lanes = e,
              i.child = null,
              i.subtreeFlags = 0,
              i.memoizedProps = null,
              i.memoizedState = null,
              i.updateQueue = null,
              i.dependencies = null,
              i.stateNode = null
            ) : (
              i.childLanes = s.childLanes,
              i.lanes = s.lanes,
              i.child = s.child,
              i.subtreeFlags = 0,
              i.deletions = null,
              i.memoizedProps = s.memoizedProps,
              i.memoizedState = s.memoizedState,
              i.updateQueue = s.updateQueue,
              i.type = s.type,
              e = s.dependencies,
              i.dependencies = e === null ? null : {
                lanes: e.lanes,
                firstContext: e.firstContext
              }
            ),
            n = n.sibling;
            return O(A, A.current & 1 | 2),
            t.child
          }
          e = e.sibling
        }
        i.tail !== null &&
        Q() > ln &&
        (t.flags |= 128, r = !0, yn(i, !1), t.lanes = 4194304)
      } else {
        if (!r) if (e = Yr(s), e !== null) {
          if (
            t.flags |= 128,
            r = !0,
            n = e.updateQueue,
            n !== null &&
            (t.updateQueue = n, t.flags |= 4),
            yn(i, !0),
            i.tail === null &&
            i.tailMode === 'hidden' &&
            !s.alternate &&
            !U
          ) return re(t),
          null
        } else 2 * Q() - i.renderingStartTime > ln &&
        n !== 1073741824 &&
        (t.flags |= 128, r = !0, yn(i, !1), t.lanes = 4194304);
        i.isBackwards ? (s.sibling = t.child, t.child = s) : (n = i.last, n !== null ? n.sibling = s : t.child = s, i.last = s)
      }
      return i.tail !== null ? (
        t = i.tail,
        i.rendering = t,
        i.tail = t.sibling,
        i.renderingStartTime = Q(),
        t.sibling = null,
        n = A.current,
        O(A, r ? n & 1 | 2 : n & 1),
        t
      ) : (re(t), null);
    case 22:
    case 23:
      return Ps(),
      r = t.memoizedState !== null,
      e !== null &&
      e.memoizedState !== null !== r &&
      (t.flags |= 8192),
      r &&
      t.mode & 1 ? he & 1073741824 &&
      (re(t), t.subtreeFlags & 6 && (t.flags |= 8192)) : re(t),
      null;
    case 24:
      return null;
    case 25:
      return null
  }
  throw Error(g(156, t.tag))
}
function xf(e, t) {
  switch (os(t), t.tag) {
    case 1:
      return pe(t.type) &&
      Hr(),
      e = t.flags,
      e & 65536 ? (t.flags = e & - 65537 | 128, t) : null;
    case 3:
      return nn(),
      I(fe),
      I(ie),
      vs(),
      e = t.flags,
      e & 65536 &&
      !(e & 128) ? (t.flags = e & - 65537 | 128, t) : null;
    case 5:
      return hs(t),
      null;
    case 13:
      if (I(A), e = t.memoizedState, e !== null && e.dehydrated !== null) {
        if (t.alternate === null) throw Error(g(340));
        en()
      }
      return e = t.flags,
      e & 65536 ? (t.flags = e & - 65537 | 128, t) : null;
    case 19:
      return I(A),
      null;
    case 4:
      return nn(),
      null;
    case 10:
      return ds(t.type._context),
      null;
    case 22:
    case 23:
      return Ps(),
      null;
    case 24:
      return null;
    default:
      return null
  }
}
var yr = !1,
le = !1,
wf = typeof WeakSet == 'function' ? WeakSet : Set,
S = null;
function Wt(e, t) {
  var n = e.ref;
  if (n !== null) if (typeof n == 'function') try {
    n(null)
  } catch (r) {
    V(e, t, r)
  } else n.current = null
}
function Ti(e, t, n) {
  try {
    n()
  } catch (r) {
    V(e, t, r)
  }
}
var Do = !1;
function kf(e, t) {
  if (mi = Fr, e = Yu(), is(e)) {
    if ('selectionStart' in e) var n = {
      start: e.selectionStart,
      end: e.selectionEnd
    };
     else e: {
      n = (n = e.ownerDocument) &&
      n.defaultView ||
      window;
      var r = n.getSelection &&
      n.getSelection();
      if (r && r.rangeCount !== 0) {
        n = r.anchorNode;
        var l = r.anchorOffset,
        i = r.focusNode;
        r = r.focusOffset;
        try {
          n.nodeType,
          i.nodeType
        } catch {
          n = null;
          break e
        }
        var s = 0,
        u = - 1,
        a = - 1,
        d = 0,
        v = 0,
        h = e,
        m = null;
        t: for (; ; ) {
          for (
            var x;
            h !== n ||
            l !== 0 &&
            h.nodeType !== 3 ||
            (u = s + l),
            h !== i ||
            r !== 0 &&
            h.nodeType !== 3 ||
            (a = s + r),
            h.nodeType === 3 &&
            (s += h.nodeValue.length),
            (x = h.firstChild) !== null;
          ) m = h,
          h = x;
          for (; ; ) {
            if (h === e) break t;
            if (
              m === n &&
              ++d === l &&
              (u = s),
              m === i &&
              ++v === r &&
              (a = s),
              (x = h.nextSibling) !== null
            ) break;
            h = m,
            m = h.parentNode
          }
          h = x
        }
        n = u === - 1 ||
        a === - 1 ? null : {
          start: u,
          end: a
        }
      } else n = null
    }
    n = n ||
    {
      start: 0,
      end: 0
    }
  } else n = null;
  for (hi = {
    focusedElem: e,
    selectionRange: n
  }, Fr = !1, S = t; S !== null; ) if (t = S, e = t.child, (t.subtreeFlags & 1028) !== 0 && e !== null) e.return = t,
  S = e;
   else for (; S !== null; ) {
    t = S;
    try {
      var w = t.alternate;
      if (t.flags & 1024) switch (t.tag) {
        case 0:
        case 11:
        case 15:
          break;
        case 1:
          if (w !== null) {
            var k = w.memoizedProps,
            F = w.memoizedState,
            f = t.stateNode,
            c = f.getSnapshotBeforeUpdate(t.elementType === t.type ? k : Re(t.type, k), F);
            f.__reactInternalSnapshotBeforeUpdate = c
          }
          break;
        case 3:
          var p = t.stateNode.containerInfo;
          p.nodeType === 1 ? p.textContent = '' : p.nodeType === 9 &&
          p.documentElement &&
          p.removeChild(p.documentElement);
          break;
        case 5:
        case 6:
        case 4:
        case 17:
          break;
        default:
          throw Error(g(163))
      }
    } catch (y) {
      V(t, t.return, y)
    }
    if (e = t.sibling, e !== null) {
      e.return = t.return,
      S = e;
      break
    }
    S = t.return
  }
  return w = Do,
  Do = !1,
  w
}
function zn(e, t, n) {
  var r = t.updateQueue;
  if (r = r !== null ? r.lastEffect : null, r !== null) {
    var l = r = r.next;
    do {
      if ((l.tag & e) === e) {
        var i = l.destroy;
        l.destroy = void 0,
        i !== void 0 &&
        Ti(t, n, i)
      }
      l = l.next
    } while (l !== r)
  }
}
function dl(e, t) {
  if (t = t.updateQueue, t = t !== null ? t.lastEffect : null, t !== null) {
    var n = t = t.next;
    do {
      if ((n.tag & e) === e) {
        var r = n.create;
        n.destroy = r()
      }
      n = n.next
    } while (n !== t)
  }
}
function Li(e) {
  var t = e.ref;
  if (t !== null) {
    var n = e.stateNode;
    switch (e.tag) {
      case 5:
        e = n;
        break;
      default:
        e = n
    }
    typeof t == 'function' ? t(e) : t.current = e
  }
}
function Wa(e) {
  var t = e.alternate;
  t !== null &&
  (e.alternate = null, Wa(t)),
  e.child = null,
  e.deletions = null,
  e.sibling = null,
  e.tag === 5 &&
  (
    t = e.stateNode,
    t !== null &&
    (delete t[Fe], delete t[Bn], delete t[gi], delete t[nf], delete t[rf])
  ),
  e.stateNode = null,
  e.return = null,
  e.dependencies = null,
  e.memoizedProps = null,
  e.memoizedState = null,
  e.pendingProps = null,
  e.stateNode = null,
  e.updateQueue = null
}
function Qa(e) {
  return e.tag === 5 ||
  e.tag === 3 ||
  e.tag === 4
}
function Io(e) {
  e: for (; ; ) {
    for (; e.sibling === null; ) {
      if (e.return === null || Qa(e.return)) return null;
      e = e.return
    }
    for (
      e.sibling.return = e.return,
      e = e.sibling;
      e.tag !== 5 &&
      e.tag !== 6 &&
      e.tag !== 18;
    ) {
      if (e.flags & 2 || e.child === null || e.tag === 4) continue e;
      e.child.return = e,
      e = e.child
    }
    if (!(e.flags & 2)) return e.stateNode
  }
}
function Mi(e, t, n) {
  var r = e.tag;
  if (r === 5 || r === 6) e = e.stateNode,
  t ? n.nodeType === 8 ? n.parentNode.insertBefore(e, t) : n.insertBefore(e, t) : (
    n.nodeType === 8 ? (t = n.parentNode, t.insertBefore(e, n)) : (t = n, t.appendChild(e)),
    n = n._reactRootContainer,
    n != null ||
    t.onclick !== null ||
    (t.onclick = $r)
  );
   else if (r !== 4 && (e = e.child, e !== null)) for (Mi(e, t, n), e = e.sibling; e !== null; ) Mi(e, t, n),
  e = e.sibling
}
function Oi(e, t, n) {
  var r = e.tag;
  if (r === 5 || r === 6) e = e.stateNode,
  t ? n.insertBefore(e, t) : n.appendChild(e);
   else if (r !== 4 && (e = e.child, e !== null)) for (Oi(e, t, n), e = e.sibling; e !== null; ) Oi(e, t, n),
  e = e.sibling
}
var q = null,
ze = !1;
function Je(e, t, n) {
  for (n = n.child; n !== null; ) Ka(e, t, n),
  n = n.sibling
}
function Ka(e, t, n) {
  if (Ae && typeof Ae.onCommitFiberUnmount == 'function') try {
    Ae.onCommitFiberUnmount(rl, n)
  } catch {
  }
  switch (n.tag) {
    case 5:
      le ||
      Wt(n, t);
    case 6:
      var r = q,
      l = ze;
      q = null,
      Je(e, t, n),
      q = r,
      ze = l,
      q !== null &&
      (
        ze ? (
          e = q,
          n = n.stateNode,
          e.nodeType === 8 ? e.parentNode.removeChild(n) : e.removeChild(n)
        ) : q.removeChild(n.stateNode)
      );
      break;
    case 18:
      q !== null &&
      (
        ze ? (
          e = q,
          n = n.stateNode,
          e.nodeType === 8 ? Fl(e.parentNode, n) : e.nodeType === 1 &&
          Fl(e, n),
          Un(e)
        ) : Fl(q, n.stateNode)
      );
      break;
    case 4:
      r = q,
      l = ze,
      q = n.stateNode.containerInfo,
      ze = !0,
      Je(e, t, n),
      q = r,
      ze = l;
      break;
    case 0:
    case 11:
    case 14:
    case 15:
      if (!le && (r = n.updateQueue, r !== null && (r = r.lastEffect, r !== null))) {
        l = r = r.next;
        do {
          var i = l,
          s = i.destroy;
          i = i.tag,
          s !== void 0 &&
          (i & 2 || i & 4) &&
          Ti(n, t, s),
          l = l.next
        } while (l !== r)
      }
      Je(e, t, n);
      break;
    case 1:
      if (
        !le &&
        (
          Wt(n, t),
          r = n.stateNode,
          typeof r.componentWillUnmount == 'function'
        )
      ) try {
        r.props = n.memoizedProps,
        r.state = n.memoizedState,
        r.componentWillUnmount()
      } catch (u) {
        V(n, t, u)
      }
      Je(e, t, n);
      break;
    case 21:
      Je(e, t, n);
      break;
    case 22:
      n.mode & 1 ? (le = (r = le) || n.memoizedState !== null, Je(e, t, n), le = r) : Je(e, t, n);
      break;
    default:
      Je(e, t, n)
  }
}
function Fo(e) {
  var t = e.updateQueue;
  if (t !== null) {
    e.updateQueue = null;
    var n = e.stateNode;
    n === null &&
    (n = e.stateNode = new wf),
    t.forEach(
      function (r) {
        var l = zf.bind(null, e, r);
        n.has(r) ||
        (n.add(r), r.then(l, l))
      }
    )
  }
}
function _e(e, t) {
  var n = t.deletions;
  if (n !== null) for (var r = 0; r < n.length; r++) {
    var l = n[r];
    try {
      var i = e,
      s = t,
      u = s;
      e: for (; u !== null; ) {
        switch (u.tag) {
          case 5:
            q = u.stateNode,
            ze = !1;
            break e;
          case 3:
            q = u.stateNode.containerInfo,
            ze = !0;
            break e;
          case 4:
            q = u.stateNode.containerInfo,
            ze = !0;
            break e
        }
        u = u.return
      }
      if (q === null) throw Error(g(160));
      Ka(i, s, l),
      q = null,
      ze = !1;
      var a = l.alternate;
      a !== null &&
      (a.return = null),
      l.return = null
    } catch (d) {
      V(l, t, d)
    }
  }
  if (t.subtreeFlags & 12854) for (t = t.child; t !== null; ) Ga(t, e),
  t = t.sibling
}
function Ga(e, t) {
  var n = e.alternate,
  r = e.flags;
  switch (e.tag) {
    case 0:
    case 11:
    case 14:
    case 15:
      if (_e(t, e), De(e), r & 4) {
        try {
          zn(3, e, e.return),
          dl(3, e)
        } catch (k) {
          V(e, e.return, k)
        }
        try {
          zn(5, e, e.return)
        } catch (k) {
          V(e, e.return, k)
        }
      }
      break;
    case 1:
      _e(t, e),
      De(e),
      r & 512 &&
      n !== null &&
      Wt(n, n.return);
      break;
    case 5:
      if (_e(t, e), De(e), r & 512 && n !== null && Wt(n, n.return), e.flags & 32) {
        var l = e.stateNode;
        try {
          On(l, '')
        } catch (k) {
          V(e, e.return, k)
        }
      }
      if (r & 4 && (l = e.stateNode, l != null)) {
        var i = e.memoizedProps,
        s = n !== null ? n.memoizedProps : i,
        u = e.type,
        a = e.updateQueue;
        if (e.updateQueue = null, a !== null) try {
          u === 'input' &&
          i.type === 'radio' &&
          i.name != null &&
          hu(l, i),
          li(u, s);
          var d = li(u, i);
          for (s = 0; s < a.length; s += 2) {
            var v = a[s],
            h = a[s + 1];
            v === 'style' ? wu(l, h) : v === 'dangerouslySetInnerHTML' ? gu(l, h) : v === 'children' ? On(l, h) : Ki(l, v, h, d)
          }
          switch (u) {
            case 'input':
              bl(l, i);
              break;
            case 'textarea':
              vu(l, i);
              break;
            case 'select':
              var m = l._wrapperState.wasMultiple;
              l._wrapperState.wasMultiple = !!i.multiple;
              var x = i.value;
              x != null ? Kt(l, !!i.multiple, x, !1) : m !== !!i.multiple &&
              (
                i.defaultValue != null ? Kt(l, !!i.multiple, i.defaultValue, !0) : Kt(l, !!i.multiple, i.multiple ? [] : '', !1)
              )
          }
          l[Bn] = i
        } catch (k) {
          V(e, e.return, k)
        }
      }
      break;
    case 6:
      if (_e(t, e), De(e), r & 4) {
        if (e.stateNode === null) throw Error(g(162));
        l = e.stateNode,
        i = e.memoizedProps;
        try {
          l.nodeValue = i
        } catch (k) {
          V(e, e.return, k)
        }
      }
      break;
    case 3:
      if (_e(t, e), De(e), r & 4 && n !== null && n.memoizedState.isDehydrated) try {
        Un(t.containerInfo)
      } catch (k) {
        V(e, e.return, k)
      }
      break;
    case 4:
      _e(t, e),
      De(e);
      break;
    case 13:
      _e(t, e),
      De(e),
      l = e.child,
      l.flags & 8192 &&
      (
        i = l.memoizedState !== null,
        l.stateNode.isHidden = i,
        !i ||
        l.alternate !== null &&
        l.alternate.memoizedState !== null ||
        (Cs = Q())
      ),
      r & 4 &&
      Fo(e);
      break;
    case 22:
      if (
        v = n !== null &&
        n.memoizedState !== null,
        e.mode & 1 ? (le = (d = le) || v, _e(t, e), le = d) : _e(t, e),
        De(e),
        r & 8192
      ) {
        if (
          d = e.memoizedState !== null,
          (e.stateNode.isHidden = d) &&
          !v &&
          e.mode & 1
        ) for (S = e, v = e.child; v !== null; ) {
          for (h = S = v; S !== null; ) {
            switch (m = S, x = m.child, m.tag) {
              case 0:
              case 11:
              case 14:
              case 15:
                zn(4, m, m.return);
                break;
              case 1:
                Wt(m, m.return);
                var w = m.stateNode;
                if (typeof w.componentWillUnmount == 'function') {
                  r = m,
                  n = m.return;
                  try {
                    t = r,
                    w.props = t.memoizedProps,
                    w.state = t.memoizedState,
                    w.componentWillUnmount()
                  } catch (k) {
                    V(r, n, k)
                  }
                }
                break;
              case 5:
                Wt(m, m.return);
                break;
              case 22:
                if (m.memoizedState !== null) {
                  Ao(h);
                  continue
                }
            }
            x !== null ? (x.return = m, S = x) : Ao(h)
          }
          v = v.sibling
        }
        e: for (v = null, h = e; ; ) {
          if (h.tag === 5) {
            if (v === null) {
              v = h;
              try {
                l = h.stateNode,
                d ? (
                  i = l.style,
                  typeof i.setProperty == 'function' ? i.setProperty('display', 'none', 'important') : i.display = 'none'
                ) : (
                  u = h.stateNode,
                  a = h.memoizedProps.style,
                  s = a != null &&
                  a.hasOwnProperty('display') ? a.display : null,
                  u.style.display = xu('display', s)
                )
              } catch (k) {
                V(e, e.return, k)
              }
            }
          } else if (h.tag === 6) {
            if (v === null) try {
              h.stateNode.nodeValue = d ? '' : h.memoizedProps
            } catch (k) {
              V(e, e.return, k)
            }
          } else if (
            (h.tag !== 22 && h.tag !== 23 || h.memoizedState === null || h === e) &&
            h.child !== null
          ) {
            h.child.return = h,
            h = h.child;
            continue
          }
          if (h === e) break e;
          for (; h.sibling === null; ) {
            if (h.return === null || h.return === e) break e;
            v === h &&
            (v = null),
            h = h.return
          }
          v === h &&
          (v = null),
          h.sibling.return = h.return,
          h = h.sibling
        }
      }
      break;
    case 19:
      _e(t, e),
      De(e),
      r & 4 &&
      Fo(e);
      break;
    case 21:
      break;
    default:
      _e(t, e),
      De(e)
  }
}
function De(e) {
  var t = e.flags;
  if (t & 2) {
    try {
      e: {
        for (var n = e.return; n !== null; ) {
          if (Qa(n)) {
            var r = n;
            break e
          }
          n = n.return
        }
        throw Error(g(160))
      }
      switch (r.tag) {
        case 5:
          var l = r.stateNode;
          r.flags & 32 &&
          (On(l, ''), r.flags &= - 33);
          var i = Io(e);
          Oi(e, i, l);
          break;
        case 3:
        case 4:
          var s = r.stateNode.containerInfo,
          u = Io(e);
          Mi(e, u, s);
          break;
        default:
          throw Error(g(161))
      }
    } catch (a) {
      V(e, e.return, a)
    }
    e.flags &= - 3
  }
  t & 4096 &&
  (e.flags &= - 4097)
}
function Sf(e, t, n) {
  S = e,
  Ya(e)
}
function Ya(e, t, n) {
  for (var r = (e.mode & 1) !== 0; S !== null; ) {
    var l = S,
    i = l.child;
    if (l.tag === 22 && r) {
      var s = l.memoizedState !== null ||
      yr;
      if (!s) {
        var u = l.alternate,
        a = u !== null &&
        u.memoizedState !== null ||
        le;
        u = yr;
        var d = le;
        if (yr = s, (le = a) && !d) for (S = l; S !== null; ) s = S,
        a = s.child,
        s.tag === 22 &&
        s.memoizedState !== null ? $o(l) : a !== null ? (a.return = s, S = a) : $o(l);
        for (; i !== null; ) S = i,
        Ya(i),
        i = i.sibling;
        S = l,
        yr = u,
        le = d
      }
      Uo(e)
    } else l.subtreeFlags & 8772 &&
    i !== null ? (i.return = l, S = i) : Uo(e)
  }
}
function Uo(e) {
  for (; S !== null; ) {
    var t = S;
    if (t.flags & 8772) {
      var n = t.alternate;
      try {
        if (t.flags & 8772) switch (t.tag) {
          case 0:
          case 11:
          case 15:
            le ||
            dl(5, t);
            break;
          case 1:
            var r = t.stateNode;
            if (t.flags & 4 && !le) if (n === null) r.componentDidMount();
             else {
              var l = t.elementType === t.type ? n.memoizedProps : Re(t.type, n.memoizedProps);
              r.componentDidUpdate(l, n.memoizedState, r.__reactInternalSnapshotBeforeUpdate)
            }
            var i = t.updateQueue;
            i !== null &&
            So(t, i, r);
            break;
          case 3:
            var s = t.updateQueue;
            if (s !== null) {
              if (n = null, t.child !== null) switch (t.child.tag) {
                case 5:
                  n = t.child.stateNode;
                  break;
                case 1:
                  n = t.child.stateNode
              }
              So(t, s, n)
            }
            break;
          case 5:
            var u = t.stateNode;
            if (n === null && t.flags & 4) {
              n = u;
              var a = t.memoizedProps;
              switch (t.type) {
                case 'button':
                case 'input':
                case 'select':
                case 'textarea':
                  a.autoFocus &&
                  n.focus();
                  break;
                case 'img':
                  a.src &&
                  (n.src = a.src)
              }
            }
            break;
          case 6:
            break;
          case 4:
            break;
          case 12:
            break;
          case 13:
            if (t.memoizedState === null) {
              var d = t.alternate;
              if (d !== null) {
                var v = d.memoizedState;
                if (v !== null) {
                  var h = v.dehydrated;
                  h !== null &&
                  Un(h)
                }
              }
            }
            break;
          case 19:
          case 17:
          case 21:
          case 22:
          case 23:
          case 25:
            break;
          default:
            throw Error(g(163))
        }
        le ||
        t.flags & 512 &&
        Li(t)
      } catch (m) {
        V(t, t.return, m)
      }
    }
    if (t === e) {
      S = null;
      break
    }
    if (n = t.sibling, n !== null) {
      n.return = t.return,
      S = n;
      break
    }
    S = t.return
  }
}
function Ao(e) {
  for (; S !== null; ) {
    var t = S;
    if (t === e) {
      S = null;
      break
    }
    var n = t.sibling;
    if (n !== null) {
      n.return = t.return,
      S = n;
      break
    }
    S = t.return
  }
}
function $o(e) {
  for (; S !== null; ) {
    var t = S;
    try {
      switch (t.tag) {
        case 0:
        case 11:
        case 15:
          var n = t.return;
          try {
            dl(4, t)
          } catch (a) {
            V(t, n, a)
          }
          break;
        case 1:
          var r = t.stateNode;
          if (typeof r.componentDidMount == 'function') {
            var l = t.return;
            try {
              r.componentDidMount()
            } catch (a) {
              V(t, l, a)
            }
          }
          var i = t.return;
          try {
            Li(t)
          } catch (a) {
            V(t, i, a)
          }
          break;
        case 5:
          var s = t.return;
          try {
            Li(t)
          } catch (a) {
            V(t, s, a)
          }
      }
    } catch (a) {
      V(t, t.return, a)
    }
    if (t === e) {
      S = null;
      break
    }
    var u = t.sibling;
    if (u !== null) {
      u.return = t.return,
      S = u;
      break
    }
    S = t.return
  }
}
var Nf = Math.ceil,
Jr = Ze.ReactCurrentDispatcher,
Ns = Ze.ReactCurrentOwner,
je = Ze.ReactCurrentBatchConfig,
L = 0,
J = null,
K = null,
b = 0,
he = 0,
Qt = ht(0),
Y = 0,
Xn = null,
Rt = 0,
fl = 0,
js = 0,
Tn = null,
ce = null,
Cs = 0,
ln = 1 / 0,
He = null,
qr = !1,
Di = null,
at = null,
gr = !1,
rt = null,
br = 0,
Ln = 0,
Ii = null,
Rr = - 1,
zr = 0;
function oe() {
  return L & 6 ? Q() : Rr !== - 1 ? Rr : Rr = Q()
}
function ct(e) {
  return e.mode & 1 ? L & 2 &&
  b !== 0 ? b & - b : sf.transition !== null ? (zr === 0 && (zr = Lu()), zr) : (e = M, e !== 0 || (e = window.event, e = e === void 0 ? 16 : Au(e.type)), e) : 1
}
function Me(e, t, n, r) {
  if (50 < Ln) throw Ln = 0,
  Ii = null,
  Error(g(185));
  Jn(e, n, r),
  (!(L & 2) || e !== J) &&
  (
    e === J &&
    (!(L & 2) && (fl |= n), Y === 4 && tt(e, b)),
    me(e, r),
    n === 1 &&
    L === 0 &&
    !(t.mode & 1) &&
    (ln = Q() + 500, ul && vt())
  )
}
function me(e, t) {
  var n = e.callbackNode;
  id(e, t);
  var r = Ir(e, e === J ? b : 0);
  if (r === 0) n !== null &&
  Ys(n),
  e.callbackNode = null,
  e.callbackPriority = 0;
   else if (t = r & - r, e.callbackPriority !== t) {
    if (n != null && Ys(n), t === 1) e.tag === 0 ? lf(Ho.bind(null, e)) : la(Ho.bind(null, e)),
    ef(function () {
      !(L & 6) &&
      vt()
    }),
    n = null;
     else {
      switch (Mu(r)) {
        case 1:
          n = Ji;
          break;
        case 4:
          n = zu;
          break;
        case 16:
          n = Dr;
          break;
        case 536870912:
          n = Tu;
          break;
        default:
          n = Dr
      }
      n = nc(n, Xa.bind(null, e))
    }
    e.callbackPriority = t,
    e.callbackNode = n
  }
}
function Xa(e, t) {
  if (Rr = - 1, zr = 0, L & 6) throw Error(g(327));
  var n = e.callbackNode;
  if (Jt() && e.callbackNode !== n) return null;
  var r = Ir(e, e === J ? b : 0);
  if (r === 0) return null;
  if (r & 30 || r & e.expiredLanes || t) t = el(e, r);
   else {
    t = r;
    var l = L;
    L |= 2;
    var i = Ja();
    (J !== e || b !== t) &&
    (He = null, ln = Q() + 500, jt(e, t));
    do try {
      Ef();
      break
    } catch (u) {
      Za(e, u)
    } while (!0);
    cs(),
    Jr.current = i,
    L = l,
    K !== null ? t = 0 : (J = null, b = 0, t = Y)
  }
  if (t !== 0) {
    if (t === 2 && (l = ai(e), l !== 0 && (r = l, t = Fi(e, l))), t === 1) throw n = Xn,
    jt(e, 0),
    tt(e, r),
    me(e, Q()),
    n;
    if (t === 6) tt(e, r);
     else {
      if (
        l = e.current.alternate,
        !(r & 30) &&
        !jf(l) &&
        (t = el(e, r), t === 2 && (i = ai(e), i !== 0 && (r = i, t = Fi(e, i))), t === 1)
      ) throw n = Xn,
      jt(e, 0),
      tt(e, r),
      me(e, Q()),
      n;
      switch (e.finishedWork = l, e.finishedLanes = r, t) {
        case 0:
        case 1:
          throw Error(g(345));
        case 2:
          wt(e, ce, He);
          break;
        case 3:
          if (tt(e, r), (r & 130023424) === r && (t = Cs + 500 - Q(), 10 < t)) {
            if (Ir(e, 0) !== 0) break;
            if (l = e.suspendedLanes, (l & r) !== r) {
              oe(),
              e.pingedLanes |= e.suspendedLanes & l;
              break
            }
            e.timeoutHandle = yi(wt.bind(null, e, ce, He), t);
            break
          }
          wt(e, ce, He);
          break;
        case 4:
          if (tt(e, r), (r & 4194240) === r) break;
          for (t = e.eventTimes, l = - 1; 0 < r; ) {
            var s = 31 - Le(r);
            i = 1 << s,
            s = t[s],
            s > l &&
            (l = s),
            r &= ~i
          }
          if (
            r = l,
            r = Q() - r,
            r = (
              120 > r ? 120 : 480 > r ? 480 : 1080 > r ? 1080 : 1920 > r ? 1920 : 3000 > r ? 3000 : 4320 > r ? 4320 : 1960 * Nf(r / 1960)
            ) - r,
            10 < r
          ) {
            e.timeoutHandle = yi(wt.bind(null, e, ce, He), r);
            break
          }
          wt(e, ce, He);
          break;
        case 5:
          wt(e, ce, He);
          break;
        default:
          throw Error(g(329))
      }
    }
  }
  return me(e, Q()),
  e.callbackNode === n ? Xa.bind(null, e) : null
}
function Fi(e, t) {
  var n = Tn;
  return e.current.memoizedState.isDehydrated &&
  (jt(e, t).flags |= 256),
  e = el(e, t),
  e !== 2 &&
  (t = ce, ce = n, t !== null && Ui(t)),
  e
}
function Ui(e) {
  ce === null ? ce = e : ce.push.apply(ce, e)
}
function jf(e) {
  for (var t = e; ; ) {
    if (t.flags & 16384) {
      var n = t.updateQueue;
      if (n !== null && (n = n.stores, n !== null)) for (var r = 0; r < n.length; r++) {
        var l = n[r],
        i = l.getSnapshot;
        l = l.value;
        try {
          if (!Oe(i(), l)) return !1
        } catch {
          return !1
        }
      }
    }
    if (n = t.child, t.subtreeFlags & 16384 && n !== null) n.return = t,
    t = n;
     else {
      if (t === e) break;
      for (; t.sibling === null; ) {
        if (t.return === null || t.return === e) return !0;
        t = t.return
      }
      t.sibling.return = t.return,
      t = t.sibling
    }
  }
  return !0
}
function tt(e, t) {
  for (
    t &= ~js,
    t &= ~fl,
    e.suspendedLanes |= t,
    e.pingedLanes &= ~t,
    e = e.expirationTimes;
    0 < t;
  ) {
    var n = 31 - Le(t),
    r = 1 << n;
    e[n] = - 1,
    t &= ~r
  }
}
function Ho(e) {
  if (L & 6) throw Error(g(327));
  Jt();
  var t = Ir(e, 0);
  if (!(t & 1)) return me(e, Q()),
  null;
  var n = el(e, t);
  if (e.tag !== 0 && n === 2) {
    var r = ai(e);
    r !== 0 &&
    (t = r, n = Fi(e, r))
  }
  if (n === 1) throw n = Xn,
  jt(e, 0),
  tt(e, t),
  me(e, Q()),
  n;
  if (n === 6) throw Error(g(345));
  return e.finishedWork = e.current.alternate,
  e.finishedLanes = t,
  wt(e, ce, He),
  me(e, Q()),
  null
}
function Es(e, t) {
  var n = L;
  L |= 1;
  try {
    return e(t)
  } finally {
    L = n,
    L === 0 &&
    (ln = Q() + 500, ul && vt())
  }
}
function zt(e) {
  rt !== null &&
  rt.tag === 0 &&
  !(L & 6) &&
  Jt();
  var t = L;
  L |= 1;
  var n = je.transition,
  r = M;
  try {
    if (je.transition = null, M = 1, e) return e()
  } finally {
    M = r,
    je.transition = n,
    L = t,
    !(L & 6) &&
    vt()
  }
}
function Ps() {
  he = Qt.current,
  I(Qt)
}
function jt(e, t) {
  e.finishedWork = null,
  e.finishedLanes = 0;
  var n = e.timeoutHandle;
  if (n !== - 1 && (e.timeoutHandle = - 1, bd(n)), K !== null) for (n = K.return; n !== null; ) {
    var r = n;
    switch (os(r), r.tag) {
      case 1:
        r = r.type.childContextTypes,
        r != null &&
        Hr();
        break;
      case 3:
        nn(),
        I(fe),
        I(ie),
        vs();
        break;
      case 5:
        hs(r);
        break;
      case 4:
        nn();
        break;
      case 13:
        I(A);
        break;
      case 19:
        I(A);
        break;
      case 10:
        ds(r.type._context);
        break;
      case 22:
      case 23:
        Ps()
    }
    n = n.return
  }
  if (
    J = e,
    K = e = dt(e.current, null),
    b = he = t,
    Y = 0,
    Xn = null,
    js = fl = Rt = 0,
    ce = Tn = null,
    St !== null
  ) {
    for (t = 0; t < St.length; t++) if (n = St[t], r = n.interleaved, r !== null) {
      n.interleaved = null;
      var l = r.next,
      i = n.pending;
      if (i !== null) {
        var s = i.next;
        i.next = l,
        r.next = s
      }
      n.pending = r
    }
    St = null
  }
  return e
}
function Za(e, t) {
  do {
    var n = K;
    try {
      if (cs(), Er.current = Zr, Xr) {
        for (var r = $.memoizedState; r !== null; ) {
          var l = r.queue;
          l !== null &&
          (l.pending = null),
          r = r.next
        }
        Xr = !1
      }
      if (
        _t = 0,
        Z = G = $ = null,
        Rn = !1,
        Kn = 0,
        Ns.current = null,
        n === null ||
        n.return === null
      ) {
        Y = 1,
        Xn = t,
        K = null;
        break
      }
      e: {
        var i = e,
        s = n.return,
        u = n,
        a = t;
        if (
          t = b,
          u.flags |= 32768,
          a !== null &&
          typeof a == 'object' &&
          typeof a.then == 'function'
        ) {
          var d = a,
          v = u,
          h = v.tag;
          if (!(v.mode & 1) && (h === 0 || h === 11 || h === 15)) {
            var m = v.alternate;
            m ? (
              v.updateQueue = m.updateQueue,
              v.memoizedState = m.memoizedState,
              v.lanes = m.lanes
            ) : (v.updateQueue = null, v.memoizedState = null)
          }
          var x = _o(s);
          if (x !== null) {
            x.flags &= - 257,
            Ro(x, s, u, i, t),
            x.mode & 1 &&
            Po(i, d, t),
            t = x,
            a = d;
            var w = t.updateQueue;
            if (w === null) {
              var k = new Set;
              k.add(a),
              t.updateQueue = k
            } else w.add(a);
            break e
          } else {
            if (!(t & 1)) {
              Po(i, d, t),
              _s();
              break e
            }
            a = Error(g(426))
          }
        } else if (U && u.mode & 1) {
          var F = _o(s);
          if (F !== null) {
            !(F.flags & 65536) &&
            (F.flags |= 256),
            Ro(F, s, u, i, t),
            us(rn(a, u));
            break e
          }
        }
        i = a = rn(a, u),
        Y !== 4 &&
        (Y = 2),
        Tn === null ? Tn = [
          i
        ] : Tn.push(i),
        i = s;
        do {
          switch (i.tag) {
            case 3:
              i.flags |= 65536,
              t &= - t,
              i.lanes |= t;
              var f = Ma(i, a, t);
              ko(i, f);
              break e;
            case 1:
              u = a;
              var c = i.type,
              p = i.stateNode;
              if (
                !(i.flags & 128) &&
                (
                  typeof c.getDerivedStateFromError == 'function' ||
                  p !== null &&
                  typeof p.componentDidCatch == 'function' &&
                  (at === null || !at.has(p))
                )
              ) {
                i.flags |= 65536,
                t &= - t,
                i.lanes |= t;
                var y = Oa(i, u, t);
                ko(i, y);
                break e
              }
          }
          i = i.return
        } while (i !== null)
      }
      ba(n)
    } catch (N) {
      t = N,
      K === n &&
      n !== null &&
      (K = n = n.return);
      continue
    }
    break
  } while (!0)
}
function Ja() {
  var e = Jr.current;
  return Jr.current = Zr,
  e === null ? Zr : e
}
function _s() {
  (Y === 0 || Y === 3 || Y === 2) &&
  (Y = 4),
  J === null ||
  !(Rt & 268435455) &&
  !(fl & 268435455) ||
  tt(J, b)
}
function el(e, t) {
  var n = L;
  L |= 2;
  var r = Ja();
  (J !== e || b !== t) &&
  (He = null, jt(e, t));
  do try {
    Cf();
    break
  } catch (l) {
    Za(e, l)
  } while (!0);
  if (cs(), L = n, Jr.current = r, K !== null) throw Error(g(261));
  return J = null,
  b = 0,
  Y
}
function Cf() {
  for (; K !== null; ) qa(K)
}
function Ef() {
  for (; K !== null && !Zc(); ) qa(K)
}
function qa(e) {
  var t = tc(e.alternate, e, he);
  e.memoizedProps = e.pendingProps,
  t === null ? ba(e) : K = t,
  Ns.current = null
}
function ba(e) {
  var t = e;
  do {
    var n = t.alternate;
    if (e = t.return, t.flags & 32768) {
      if (n = xf(n, t), n !== null) {
        n.flags &= 32767,
        K = n;
        return
      }
      if (e !== null) e.flags |= 32768,
      e.subtreeFlags = 0,
      e.deletions = null;
       else {
        Y = 6,
        K = null;
        return
      }
    } else if (n = gf(n, t, he), n !== null) {
      K = n;
      return
    }
    if (t = t.sibling, t !== null) {
      K = t;
      return
    }
    K = t = e
  } while (t !== null);
  Y === 0 &&
  (Y = 5)
}
function wt(e, t, n) {
  var r = M,
  l = je.transition;
  try {
    je.transition = null,
    M = 1,
    Pf(e, t, n, r)
  } finally {
    je.transition = l,
    M = r
  }
  return null
}
function Pf(e, t, n, r) {
  do Jt();
  while (rt !== null);
  if (L & 6) throw Error(g(327));
  n = e.finishedWork;
  var l = e.finishedLanes;
  if (n === null) return null;
  if (e.finishedWork = null, e.finishedLanes = 0, n === e.current) throw Error(g(177));
  e.callbackNode = null,
  e.callbackPriority = 0;
  var i = n.lanes | n.childLanes;
  if (
    sd(e, i),
    e === J &&
    (K = J = null, b = 0),
    !(n.subtreeFlags & 2064) &&
    !(n.flags & 2064) ||
    gr ||
    (gr = !0, nc(Dr, function () {
      return Jt(),
      null
    })),
    i = (n.flags & 15990) !== 0,
    n.subtreeFlags & 15990 ||
    i
  ) {
    i = je.transition,
    je.transition = null;
    var s = M;
    M = 1;
    var u = L;
    L |= 4,
    Ns.current = null,
    kf(e, n),
    Ga(n, e),
    Kd(hi),
    Fr = !!mi,
    hi = mi = null,
    e.current = n,
    Sf(n),
    Jc(),
    L = u,
    M = s,
    je.transition = i
  } else e.current = n;
  if (
    gr &&
    (gr = !1, rt = e, br = l),
    i = e.pendingLanes,
    i === 0 &&
    (at = null),
    ed(n.stateNode),
    me(e, Q()),
    t !== null
  ) for (r = e.onRecoverableError, n = 0; n < t.length; n++) l = t[n],
  r(l.value, {
    componentStack: l.stack,
    digest: l.digest
  });
  if (qr) throw qr = !1,
  e = Di,
  Di = null,
  e;
  return br & 1 &&
  e.tag !== 0 &&
  Jt(),
  i = e.pendingLanes,
  i & 1 ? e === Ii ? Ln++ : (Ln = 0, Ii = e) : Ln = 0,
  vt(),
  null
}
function Jt() {
  if (rt !== null) {
    var e = Mu(br),
    t = je.transition,
    n = M;
    try {
      if (je.transition = null, M = 16 > e ? 16 : e, rt === null) var r = !1;
       else {
        if (e = rt, rt = null, br = 0, L & 6) throw Error(g(331));
        var l = L;
        for (L |= 4, S = e.current; S !== null; ) {
          var i = S,
          s = i.child;
          if (S.flags & 16) {
            var u = i.deletions;
            if (u !== null) {
              for (var a = 0; a < u.length; a++) {
                var d = u[a];
                for (S = d; S !== null; ) {
                  var v = S;
                  switch (v.tag) {
                    case 0:
                    case 11:
                    case 15:
                      zn(8, v, i)
                  }
                  var h = v.child;
                  if (h !== null) h.return = v,
                  S = h;
                   else for (; S !== null; ) {
                    v = S;
                    var m = v.sibling,
                    x = v.return;
                    if (Wa(v), v === d) {
                      S = null;
                      break
                    }
                    if (m !== null) {
                      m.return = x,
                      S = m;
                      break
                    }
                    S = x
                  }
                }
              }
              var w = i.alternate;
              if (w !== null) {
                var k = w.child;
                if (k !== null) {
                  w.child = null;
                  do {
                    var F = k.sibling;
                    k.sibling = null,
                    k = F
                  } while (k !== null)
                }
              }
              S = i
            }
          }
          if (i.subtreeFlags & 2064 && s !== null) s.return = i,
          S = s;
           else e: for (; S !== null; ) {
            if (i = S, i.flags & 2048) switch (i.tag) {
              case 0:
              case 11:
              case 15:
                zn(9, i, i.return)
            }
            var f = i.sibling;
            if (f !== null) {
              f.return = i.return,
              S = f;
              break e
            }
            S = i.return
          }
        }
        var c = e.current;
        for (S = c; S !== null; ) {
          s = S;
          var p = s.child;
          if (s.subtreeFlags & 2064 && p !== null) p.return = s,
          S = p;
           else e: for (s = c; S !== null; ) {
            if (u = S, u.flags & 2048) try {
              switch (u.tag) {
                case 0:
                case 11:
                case 15:
                  dl(9, u)
              }
            } catch (N) {
              V(u, u.return, N)
            }
            if (u === s) {
              S = null;
              break e
            }
            var y = u.sibling;
            if (y !== null) {
              y.return = u.return,
              S = y;
              break e
            }
            S = u.return
          }
        }
        if (L = l, vt(), Ae && typeof Ae.onPostCommitFiberRoot == 'function') try {
          Ae.onPostCommitFiberRoot(rl, e)
        } catch {
        }
        r = !0
      }
      return r
    } finally {
      M = n,
      je.transition = t
    }
  }
  return !1
}
function Vo(e, t, n) {
  t = rn(n, t),
  t = Ma(e, t, 1),
  e = ut(e, t, 1),
  t = oe(),
  e !== null &&
  (Jn(e, 1, t), me(e, t))
}
function V(e, t, n) {
  if (e.tag === 3) Vo(e, e, n);
   else for (; t !== null; ) {
    if (t.tag === 3) {
      Vo(t, e, n);
      break
    } else if (t.tag === 1) {
      var r = t.stateNode;
      if (
        typeof t.type.getDerivedStateFromError == 'function' ||
        typeof r.componentDidCatch == 'function' &&
        (at === null || !at.has(r))
      ) {
        e = rn(n, e),
        e = Oa(t, e, 1),
        t = ut(t, e, 1),
        e = oe(),
        t !== null &&
        (Jn(t, 1, e), me(t, e));
        break
      }
    }
    t = t.return
  }
}
function _f(e, t, n) {
  var r = e.pingCache;
  r !== null &&
  r.delete(t),
  t = oe(),
  e.pingedLanes |= e.suspendedLanes & n,
  J === e &&
  (b & n) === n &&
  (Y === 4 || Y === 3 && (b & 130023424) === b && 500 > Q() - Cs ? jt(e, 0) : js |= n),
  me(e, t)
}
function ec(e, t) {
  t === 0 &&
  (e.mode & 1 ? (t = ur, ur <<= 1, !(ur & 130023424) && (ur = 4194304)) : t = 1);
  var n = oe();
  e = Ye(e, t),
  e !== null &&
  (Jn(e, t, n), me(e, n))
}
function Rf(e) {
  var t = e.memoizedState,
  n = 0;
  t !== null &&
  (n = t.retryLane),
  ec(e, n)
}
function zf(e, t) {
  var n = 0;
  switch (e.tag) {
    case 13:
      var r = e.stateNode,
      l = e.memoizedState;
      l !== null &&
      (n = l.retryLane);
      break;
    case 19:
      r = e.stateNode;
      break;
    default:
      throw Error(g(314))
  }
  r !== null &&
  r.delete(t),
  ec(e, n)
}
var tc;
tc = function (e, t, n) {
  if (e !== null) if (e.memoizedProps !== t.pendingProps || fe.current) de = !0;
   else {
    if (!(e.lanes & n) && !(t.flags & 128)) return de = !1,
    yf(e, t, n);
    de = !!(e.flags & 131072)
  } else de = !1,
  U &&
  t.flags & 1048576 &&
  ia(t, Wr, t.index);
  switch (t.lanes = 0, t.tag) {
    case 2:
      var r = t.type;
      _r(e, t),
      e = t.pendingProps;
      var l = bt(t, ie.current);
      Zt(t, n),
      l = gs(null, t, r, e, l, n);
      var i = xs();
      return t.flags |= 1,
      typeof l == 'object' &&
      l !== null &&
      typeof l.render == 'function' &&
      l.$$typeof === void 0 ? (
        t.tag = 1,
        t.memoizedState = null,
        t.updateQueue = null,
        pe(r) ? (i = !0, Vr(t)) : i = !1,
        t.memoizedState = l.state !== null &&
        l.state !== void 0 ? l.state : null,
        ps(t),
        l.updater = cl,
        t.stateNode = l,
        l._reactInternals = t,
        ji(t, r, e, n),
        t = Pi(null, t, r, !0, i, n)
      ) : (t.tag = 0, U && i && ss(t), se(null, t, l, n), t = t.child),
      t;
    case 16:
      r = t.elementType;
      e: {
        switch (
            _r(e, t),
            e = t.pendingProps,
            l = r._init,
            r = l(r._payload),
            t.type = r,
            l = t.tag = Lf(r),
            e = Re(r, e),
            l
          ) {
          case 0:
            t = Ei(null, t, r, e, n);
            break e;
          case 1:
            t = Lo(null, t, r, e, n);
            break e;
          case 11:
            t = zo(null, t, r, e, n);
            break e;
          case 14:
            t = To(null, t, r, Re(r.type, e), n);
            break e
        }
        throw Error(g(306, r, ''))
      }
      return t;
    case 0:
      return r = t.type,
      l = t.pendingProps,
      l = t.elementType === r ? l : Re(r, l),
      Ei(e, t, r, l, n);
    case 1:
      return r = t.type,
      l = t.pendingProps,
      l = t.elementType === r ? l : Re(r, l),
      Lo(e, t, r, l, n);
    case 3:
      e: {
        if (Ua(t), e === null) throw Error(g(387));
        r = t.pendingProps,
        i = t.memoizedState,
        l = i.element,
        da(e, t),
        Gr(t, r, null, n);
        var s = t.memoizedState;
        if (r = s.element, i.isDehydrated) if (
          i = {
            element: r,
            isDehydrated: !1,
            cache: s.cache,
            pendingSuspenseBoundaries: s.pendingSuspenseBoundaries,
            transitions: s.transitions
          },
          t.updateQueue.baseState = i,
          t.memoizedState = i,
          t.flags & 256
        ) {
          l = rn(Error(g(423)), t),
          t = Mo(e, t, r, n, l);
          break e
        } else if (r !== l) {
          l = rn(Error(g(424)), t),
          t = Mo(e, t, r, n, l);
          break e
        } else for (
          ve = ot(t.stateNode.containerInfo.firstChild),
          ye = t,
          U = !0,
          Te = null,
          n = aa(t, null, r, n),
          t.child = n;
          n;
        ) n.flags = n.flags & - 3 | 4096,
        n = n.sibling;
         else {
          if (en(), r === l) {
            t = Xe(e, t, n);
            break e
          }
          se(e, t, r, n)
        }
        t = t.child
      }
      return t;
    case 5:
      return fa(t),
      e === null &&
      ki(t),
      r = t.type,
      l = t.pendingProps,
      i = e !== null ? e.memoizedProps : null,
      s = l.children,
      vi(r, l) ? s = null : i !== null &&
      vi(r, i) &&
      (t.flags |= 32),
      Fa(e, t),
      se(e, t, s, n),
      t.child;
    case 6:
      return e === null &&
      ki(t),
      null;
    case 13:
      return Aa(e, t, n);
    case 4:
      return ms(t, t.stateNode.containerInfo),
      r = t.pendingProps,
      e === null ? t.child = tn(t, null, r, n) : se(e, t, r, n),
      t.child;
    case 11:
      return r = t.type,
      l = t.pendingProps,
      l = t.elementType === r ? l : Re(r, l),
      zo(e, t, r, l, n);
    case 7:
      return se(e, t, t.pendingProps, n),
      t.child;
    case 8:
      return se(e, t, t.pendingProps.children, n),
      t.child;
    case 12:
      return se(e, t, t.pendingProps.children, n),
      t.child;
    case 10:
      e: {
        if (
          r = t.type._context,
          l = t.pendingProps,
          i = t.memoizedProps,
          s = l.value,
          O(Qr, r._currentValue),
          r._currentValue = s,
          i !== null
        ) if (Oe(i.value, s)) {
          if (i.children === l.children && !fe.current) {
            t = Xe(e, t, n);
            break e
          }
        } else for (i = t.child, i !== null && (i.return = t); i !== null; ) {
          var u = i.dependencies;
          if (u !== null) {
            s = i.child;
            for (var a = u.firstContext; a !== null; ) {
              if (a.context === r) {
                if (i.tag === 1) {
                  a = Qe( - 1, n & - n),
                  a.tag = 2;
                  var d = i.updateQueue;
                  if (d !== null) {
                    d = d.shared;
                    var v = d.pending;
                    v === null ? a.next = a : (a.next = v.next, v.next = a),
                    d.pending = a
                  }
                }
                i.lanes |= n,
                a = i.alternate,
                a !== null &&
                (a.lanes |= n),
                Si(i.return, n, t),
                u.lanes |= n;
                break
              }
              a = a.next
            }
          } else if (i.tag === 10) s = i.type === t.type ? null : i.child;
           else if (i.tag === 18) {
            if (s = i.return, s === null) throw Error(g(341));
            s.lanes |= n,
            u = s.alternate,
            u !== null &&
            (u.lanes |= n),
            Si(s, n, t),
            s = i.sibling
          } else s = i.child;
          if (s !== null) s.return = i;
           else for (s = i; s !== null; ) {
            if (s === t) {
              s = null;
              break
            }
            if (i = s.sibling, i !== null) {
              i.return = s.return,
              s = i;
              break
            }
            s = s.return
          }
          i = s
        }
        se(e, t, l.children, n),
        t = t.child
      }
      return t;
    case 9:
      return l = t.type,
      r = t.pendingProps.children,
      Zt(t, n),
      l = Ce(l),
      r = r(l),
      t.flags |= 1,
      se(e, t, r, n),
      t.child;
    case 14:
      return r = t.type,
      l = Re(r, t.pendingProps),
      l = Re(r.type, l),
      To(e, t, r, l, n);
    case 15:
      return Da(e, t, t.type, t.pendingProps, n);
    case 17:
      return r = t.type,
      l = t.pendingProps,
      l = t.elementType === r ? l : Re(r, l),
      _r(e, t),
      t.tag = 1,
      pe(r) ? (e = !0, Vr(t)) : e = !1,
      Zt(t, n),
      La(t, r, l),
      ji(t, r, l, n),
      Pi(null, t, r, !0, e, n);
    case 19:
      return $a(e, t, n);
    case 22:
      return Ia(e, t, n)
  }
  throw Error(g(156, t.tag))
};
function nc(e, t) {
  return Ru(e, t)
}
function Tf(e, t, n, r) {
  this.tag = e,
  this.key = n,
  this.sibling = this.child = this.return = this.stateNode = this.type = this.elementType = null,
  this.index = 0,
  this.ref = null,
  this.pendingProps = t,
  this.dependencies = this.memoizedState = this.updateQueue = this.memoizedProps = null,
  this.mode = r,
  this.subtreeFlags = this.flags = 0,
  this.deletions = null,
  this.childLanes = this.lanes = 0,
  this.alternate = null
}
function Ne(e, t, n, r) {
  return new Tf(e, t, n, r)
}
function Rs(e) {
  return e = e.prototype,
  !(!e || !e.isReactComponent)
}
function Lf(e) {
  if (typeof e == 'function') return Rs(e) ? 1 : 0;
  if (e != null) {
    if (e = e.$$typeof, e === Yi) return 11;
    if (e === Xi) return 14
  }
  return 2
}
function dt(e, t) {
  var n = e.alternate;
  return n === null ? (
    n = Ne(e.tag, t, e.key, e.mode),
    n.elementType = e.elementType,
    n.type = e.type,
    n.stateNode = e.stateNode,
    n.alternate = e,
    e.alternate = n
  ) : (
    n.pendingProps = t,
    n.type = e.type,
    n.flags = 0,
    n.subtreeFlags = 0,
    n.deletions = null
  ),
  n.flags = e.flags & 14680064,
  n.childLanes = e.childLanes,
  n.lanes = e.lanes,
  n.child = e.child,
  n.memoizedProps = e.memoizedProps,
  n.memoizedState = e.memoizedState,
  n.updateQueue = e.updateQueue,
  t = e.dependencies,
  n.dependencies = t === null ? null : {
    lanes: t.lanes,
    firstContext: t.firstContext
  },
  n.sibling = e.sibling,
  n.index = e.index,
  n.ref = e.ref,
  n
}
function Tr(e, t, n, r, l, i) {
  var s = 2;
  if (r = e, typeof e == 'function') Rs(e) &&
  (s = 1);
   else if (typeof e == 'string') s = 5;
   else e: switch (e) {
    case Dt:
      return Ct(n.children, l, i, t);
    case Gi:
      s = 8,
      l |= 8;
      break;
    case Yl:
      return e = Ne(12, n, t, l | 2),
      e.elementType = Yl,
      e.lanes = i,
      e;
    case Xl:
      return e = Ne(13, n, t, l),
      e.elementType = Xl,
      e.lanes = i,
      e;
    case Zl:
      return e = Ne(19, n, t, l),
      e.elementType = Zl,
      e.lanes = i,
      e;
    case fu:
      return pl(n, l, i, t);
    default:
      if (typeof e == 'object' && e !== null) switch (e.$$typeof) {
        case cu:
          s = 10;
          break e;
        case du:
          s = 9;
          break e;
        case Yi:
          s = 11;
          break e;
        case Xi:
          s = 14;
          break e;
        case qe:
          s = 16,
          r = null;
          break e
      }
      throw Error(g(130, e == null ? e : typeof e, ''))
  }
  return t = Ne(s, n, t, l),
  t.elementType = e,
  t.type = r,
  t.lanes = i,
  t
}
function Ct(e, t, n, r) {
  return e = Ne(7, e, r, t),
  e.lanes = n,
  e
}
function pl(e, t, n, r) {
  return e = Ne(22, e, r, t),
  e.elementType = fu,
  e.lanes = n,
  e.stateNode = {
    isHidden: !1
  },
  e
}
function Ql(e, t, n) {
  return e = Ne(6, e, null, t),
  e.lanes = n,
  e
}
function Kl(e, t, n) {
  return t = Ne(4, e.children !== null ? e.children : [], e.key, t),
  t.lanes = n,
  t.stateNode = {
    containerInfo: e.containerInfo,
    pendingChildren: null,
    implementation: e.implementation
  },
  t
}
function Mf(e, t, n, r, l) {
  this.tag = t,
  this.containerInfo = e,
  this.finishedWork = this.pingCache = this.current = this.pendingChildren = null,
  this.timeoutHandle = - 1,
  this.callbackNode = this.pendingContext = this.context = null,
  this.callbackPriority = 0,
  this.eventTimes = El(0),
  this.expirationTimes = El( - 1),
  this.entangledLanes = this.finishedLanes = this.mutableReadLanes = this.expiredLanes = this.pingedLanes = this.suspendedLanes = this.pendingLanes = 0,
  this.entanglements = El(0),
  this.identifierPrefix = r,
  this.onRecoverableError = l,
  this.mutableSourceEagerHydrationData = null
}
function zs(e, t, n, r, l, i, s, u, a) {
  return e = new Mf(e, t, n, u, a),
  t === 1 ? (t = 1, i === !0 && (t |= 8)) : t = 0,
  i = Ne(3, null, null, t),
  e.current = i,
  i.stateNode = e,
  i.memoizedState = {
    element: r,
    isDehydrated: n,
    cache: null,
    transitions: null,
    pendingSuspenseBoundaries: null
  },
  ps(i),
  e
}
function Of(e, t, n) {
  var r = 3 < arguments.length &&
  arguments[3] !== void 0 ? arguments[3] : null;
  return {
    $$typeof: Ot,
    key: r == null ? null : '' + r,
    children: e,
    containerInfo: t,
    implementation: n
  }
}
function rc(e) {
  if (!e) return pt;
  e = e._reactInternals;
  e: {
    if (Lt(e) !== e || e.tag !== 1) throw Error(g(170));
    var t = e;
    do {
      switch (t.tag) {
        case 3:
          t = t.stateNode.context;
          break e;
        case 1:
          if (pe(t.type)) {
            t = t.stateNode.__reactInternalMemoizedMergedChildContext;
            break e
          }
      }
      t = t.return
    } while (t !== null);
    throw Error(g(171))
  }
  if (e.tag === 1) {
    var n = e.type;
    if (pe(n)) return ra(e, n, t)
  }
  return t
}
function lc(e, t, n, r, l, i, s, u, a) {
  return e = zs(n, r, !0, e, l, i, s, u, a),
  e.context = rc(null),
  n = e.current,
  r = oe(),
  l = ct(n),
  i = Qe(r, l),
  i.callback = t ?? null,
  ut(n, i, l),
  e.current.lanes = l,
  Jn(e, l, r),
  me(e, r),
  e
}
function ml(e, t, n, r) {
  var l = t.current,
  i = oe(),
  s = ct(l);
  return n = rc(n),
  t.context === null ? t.context = n : t.pendingContext = n,
  t = Qe(i, s),
  t.payload = {
    element: e
  },
  r = r === void 0 ? null : r,
  r !== null &&
  (t.callback = r),
  e = ut(l, t, s),
  e !== null &&
  (Me(e, l, s, i), Cr(e, l, s)),
  s
}
function tl(e) {
  if (e = e.current, !e.child) return null;
  switch (e.child.tag) {
    case 5:
      return e.child.stateNode;
    default:
      return e.child.stateNode
  }
}
function Bo(e, t) {
  if (e = e.memoizedState, e !== null && e.dehydrated !== null) {
    var n = e.retryLane;
    e.retryLane = n !== 0 &&
    n < t ? n : t
  }
}
function Ts(e, t) {
  Bo(e, t),
  (e = e.alternate) &&
  Bo(e, t)
}
function Df() {
  return null
}
var ic = typeof reportError == 'function' ? reportError : function (e) {
  console.error(e)
};
function Ls(e) {
  this._internalRoot = e
}
hl.prototype.render = Ls.prototype.render = function (e) {
  var t = this._internalRoot;
  if (t === null) throw Error(g(409));
  ml(e, t, null, null)
};
hl.prototype.unmount = Ls.prototype.unmount = function () {
  var e = this._internalRoot;
  if (e !== null) {
    this._internalRoot = null;
    var t = e.containerInfo;
    zt(function () {
      ml(null, e, null, null)
    }),
    t[Ge] = null
  }
};
function hl(e) {
  this._internalRoot = e
}
hl.prototype.unstable_scheduleHydration = function (e) {
  if (e) {
    var t = Iu();
    e = {
      blockedOn: null,
      target: e,
      priority: t
    };
    for (var n = 0; n < et.length && t !== 0 && t < et[n].priority; n++);
    et.splice(n, 0, e),
    n === 0 &&
    Uu(e)
  }
};
function Ms(e) {
  return !(!e || e.nodeType !== 1 && e.nodeType !== 9 && e.nodeType !== 11)
}
function vl(e) {
  return !(
    !e ||
    e.nodeType !== 1 &&
    e.nodeType !== 9 &&
    e.nodeType !== 11 &&
    (e.nodeType !== 8 || e.nodeValue !== ' react-mount-point-unstable ')
  )
}
function Wo() {
}
function If(e, t, n, r, l) {
  if (l) {
    if (typeof r == 'function') {
      var i = r;
      r = function () {
        var d = tl(s);
        i.call(d)
      }
    }
    var s = lc(t, r, e, 0, null, !1, !1, '', Wo);
    return e._reactRootContainer = s,
    e[Ge] = s.current,
    Hn(e.nodeType === 8 ? e.parentNode : e),
    zt(),
    s
  }
  for (; l = e.lastChild; ) e.removeChild(l);
  if (typeof r == 'function') {
    var u = r;
    r = function () {
      var d = tl(a);
      u.call(d)
    }
  }
  var a = zs(e, 0, !1, null, null, !1, !1, '', Wo);
  return e._reactRootContainer = a,
  e[Ge] = a.current,
  Hn(e.nodeType === 8 ? e.parentNode : e),
  zt(function () {
    ml(t, a, n, r)
  }),
  a
}
function yl(e, t, n, r, l) {
  var i = n._reactRootContainer;
  if (i) {
    var s = i;
    if (typeof l == 'function') {
      var u = l;
      l = function () {
        var a = tl(s);
        u.call(a)
      }
    }
    ml(t, s, e, l)
  } else s = If(n, t, e, l, r);
  return tl(s)
}
Ou = function (e) {
  switch (e.tag) {
    case 3:
      var t = e.stateNode;
      if (t.current.memoizedState.isDehydrated) {
        var n = kn(t.pendingLanes);
        n !== 0 &&
        (qi(t, n | 1), me(t, Q()), !(L & 6) && (ln = Q() + 500, vt()))
      }
      break;
    case 13:
      zt(function () {
        var r = Ye(e, 1);
        if (r !== null) {
          var l = oe();
          Me(r, e, 1, l)
        }
      }),
      Ts(e, 1)
  }
};
bi = function (e) {
  if (e.tag === 13) {
    var t = Ye(e, 134217728);
    if (t !== null) {
      var n = oe();
      Me(t, e, 134217728, n)
    }
    Ts(e, 134217728)
  }
};
Du = function (e) {
  if (e.tag === 13) {
    var t = ct(e),
    n = Ye(e, t);
    if (n !== null) {
      var r = oe();
      Me(n, e, t, r)
    }
    Ts(e, t)
  }
};
Iu = function () {
  return M
};
Fu = function (e, t) {
  var n = M;
  try {
    return M = e,
    t()
  } finally {
    M = n
  }
};
si = function (e, t, n) {
  switch (t) {
    case 'input':
      if (bl(e, n), t = n.name, n.type === 'radio' && t != null) {
        for (n = e; n.parentNode; ) n = n.parentNode;
        for (
          n = n.querySelectorAll('input[name=' + JSON.stringify('' + t) + '][type="radio"]'),
          t = 0;
          t < n.length;
          t++
        ) {
          var r = n[t];
          if (r !== e && r.form === e.form) {
            var l = ol(r);
            if (!l) throw Error(g(90));
            mu(r),
            bl(r, l)
          }
        }
      }
      break;
    case 'textarea':
      vu(e, n);
      break;
    case 'select':
      t = n.value,
      t != null &&
      Kt(e, !!n.multiple, t, !1)
  }
};
Nu = Es;
ju = zt;
var Ff = {
  usingClientEntryPoint: !1,
  Events: [
    bn,
    At,
    ol,
    ku,
    Su,
    Es
  ]
},
gn = {
  findFiberByHostInstance: kt,
  bundleType: 0,
  version: '18.3.1',
  rendererPackageName: 'react-dom'
},
Uf = {
  bundleType: gn.bundleType,
  version: gn.version,
  rendererPackageName: gn.rendererPackageName,
  rendererConfig: gn.rendererConfig,
  overrideHookState: null,
  overrideHookStateDeletePath: null,
  overrideHookStateRenamePath: null,
  overrideProps: null,
  overridePropsDeletePath: null,
  overridePropsRenamePath: null,
  setErrorHandler: null,
  setSuspenseHandler: null,
  scheduleUpdate: null,
  currentDispatcherRef: Ze.ReactCurrentDispatcher,
  findHostInstanceByFiber: function (e) {
    return e = Pu(e),
    e === null ? null : e.stateNode
  },
  findFiberByHostInstance: gn.findFiberByHostInstance ||
  Df,
  findHostInstancesForRefresh: null,
  scheduleRefresh: null,
  scheduleRoot: null,
  setRefreshHandler: null,
  getCurrentFiber: null,
  reconcilerVersion: '18.3.1-next-f1338f8080-20240426'
};
if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < 'u') {
  var xr = __REACT_DEVTOOLS_GLOBAL_HOOK__;
  if (!xr.isDisabled && xr.supportsFiber) try {
    rl = xr.inject(Uf),
    Ae = xr
  } catch {
  }
}
xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = Ff;
xe.createPortal = function (e, t) {
  var n = 2 < arguments.length &&
  arguments[2] !== void 0 ? arguments[2] : null;
  if (!Ms(t)) throw Error(g(200));
  return Of(e, t, null, n)
};
xe.createRoot = function (e, t) {
  if (!Ms(e)) throw Error(g(299));
  var n = !1,
  r = '',
  l = ic;
  return t != null &&
  (
    t.unstable_strictMode === !0 &&
    (n = !0),
    t.identifierPrefix !== void 0 &&
    (r = t.identifierPrefix),
    t.onRecoverableError !== void 0 &&
    (l = t.onRecoverableError)
  ),
  t = zs(e, 1, !1, null, null, n, !1, r, l),
  e[Ge] = t.current,
  Hn(e.nodeType === 8 ? e.parentNode : e),
  new Ls(t)
};
xe.findDOMNode = function (e) {
  if (e == null) return null;
  if (e.nodeType === 1) return e;
  var t = e._reactInternals;
  if (t === void 0) throw typeof e.render == 'function' ? Error(g(188)) : (e = Object.keys(e).join(','), Error(g(268, e)));
  return e = Pu(t),
  e = e === null ? null : e.stateNode,
  e
};
xe.flushSync = function (e) {
  return zt(e)
};
xe.hydrate = function (e, t, n) {
  if (!vl(t)) throw Error(g(200));
  return yl(null, e, t, !0, n)
};
xe.hydrateRoot = function (e, t, n) {
  if (!Ms(e)) throw Error(g(405));
  var r = n != null &&
  n.hydratedSources ||
  null,
  l = !1,
  i = '',
  s = ic;
  if (
    n != null &&
    (
      n.unstable_strictMode === !0 &&
      (l = !0),
      n.identifierPrefix !== void 0 &&
      (i = n.identifierPrefix),
      n.onRecoverableError !== void 0 &&
      (s = n.onRecoverableError)
    ),
    t = lc(t, null, e, 1, n ?? null, l, !1, i, s),
    e[Ge] = t.current,
    Hn(e),
    r
  ) for (e = 0; e < r.length; e++) n = r[e],
  l = n._getVersion,
  l = l(n._source),
  t.mutableSourceEagerHydrationData == null ? t.mutableSourceEagerHydrationData = [
    n,
    l
  ] : t.mutableSourceEagerHydrationData.push(n, l);
  return new hl(t)
};
xe.render = function (e, t, n) {
  if (!vl(t)) throw Error(g(200));
  return yl(null, e, t, !1, n)
};
xe.unmountComponentAtNode = function (e) {
  if (!vl(e)) throw Error(g(40));
  return e._reactRootContainer ? (
    zt(
      function () {
        yl(
          null,
          null,
          e,
          !1,
          function () {
            e._reactRootContainer = null,
            e[Ge] = null
          }
        )
      }
    ),
    !0
  ) : !1
};
xe.unstable_batchedUpdates = Es;
xe.unstable_renderSubtreeIntoContainer = function (e, t, n, r) {
  if (!vl(n)) throw Error(g(200));
  if (e == null || e._reactInternals === void 0) throw Error(g(38));
  return yl(e, t, n, !1, r)
};
xe.version = '18.3.1-next-f1338f8080-20240426';
function sc() {
  if (
    !(
      typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ > 'u' ||
      typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE != 'function'
    )
  ) try {
    __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(sc)
  } catch (e) {
    console.error(e)
  }
}
sc(),
su.exports = xe;
var Af = su.exports,
oc,
Qo = Af;
oc = Qo.createRoot,
Qo.hydrateRoot; /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
var $f = {
  xmlns: 'http://www.w3.org/2000/svg',
  width: 24,
  height: 24,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round'
}; /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Hf = e => e.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase().trim(),
te = (e, t) => {
  const n = Ue.forwardRef(
    ({
      color: r = 'currentColor',
      size: l = 24,
      strokeWidth: i = 2,
      absoluteStrokeWidth: s,
      className: u = '',
      children: a,
      ...d
    }, v) => Ue.createElement(
      'svg',
      {
        ref: v,
        ...$f,
        width: l,
        height: l,
        stroke: r,
        strokeWidth: s ? Number(i) * 24 / Number(l) : i,
        className: [
          'lucide',
          `lucide-${ Hf(e) }`,
          u
        ].join(' '),
        ...d
      },
      [
        ...t.map(([h,
        m]) => Ue.createElement(h, m)),
        ...Array.isArray(a) ? a : [
          a
        ]
      ]
    )
  );
  return n.displayName = `${ e }`,
  n
}; /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Os = te(
  'Activity',
  [
    ['path',
    {
      d: 'M22 12h-4l-3 9L9 3l-3 9H2',
      key: 'd5dnw9'
    }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Ko = te(
  'AlertCircle',
  [
    ['circle',
    {
      cx: '12',
      cy: '12',
      r: '10',
      key: '1mglay'
    }
    ],
    [
      'line',
      {
        x1: '12',
        x2: '12',
        y1: '8',
        y2: '12',
        key: '1pkeuh'
      }
    ],
    [
      'line',
      {
        x1: '12',
        x2: '12.01',
        y1: '16',
        y2: '16',
        key: '4dfq90'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Vf = te(
  'BarChart3',
  [
    ['path',
    {
      d: 'M3 3v18h18',
      key: '1s2lah'
    }
    ],
    [
      'path',
      {
        d: 'M18 17V9',
        key: '2bz60n'
      }
    ],
    [
      'path',
      {
        d: 'M13 17V5',
        key: '1frdt8'
      }
    ],
    [
      'path',
      {
        d: 'M8 17v-3',
        key: '17ska0'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Go = te(
  'CheckCircle',
  [
    ['path',
    {
      d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14',
      key: 'g774vq'
    }
    ],
    [
      'path',
      {
        d: 'm9 11 3 3L22 4',
        key: '1pflzl'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const uc = te(
  'Clock',
  [
    ['circle',
    {
      cx: '12',
      cy: '12',
      r: '10',
      key: '1mglay'
    }
    ],
    [
      'polyline',
      {
        points: '12 6 12 12 16 14',
        key: '68esgv'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Bf = te(
  'Cpu',
  [
    ['rect',
    {
      x: '4',
      y: '4',
      width: '16',
      height: '16',
      rx: '2',
      key: '1vbyd7'
    }
    ],
    [
      'rect',
      {
        x: '9',
        y: '9',
        width: '6',
        height: '6',
        key: 'o3kz5p'
      }
    ],
    [
      'path',
      {
        d: 'M15 2v2',
        key: '13l42r'
      }
    ],
    [
      'path',
      {
        d: 'M15 20v2',
        key: '15mkzm'
      }
    ],
    [
      'path',
      {
        d: 'M2 15h2',
        key: '1gxd5l'
      }
    ],
    [
      'path',
      {
        d: 'M2 9h2',
        key: '1bbxkp'
      }
    ],
    [
      'path',
      {
        d: 'M20 15h2',
        key: '19e6y8'
      }
    ],
    [
      'path',
      {
        d: 'M20 9h2',
        key: '19tzq7'
      }
    ],
    [
      'path',
      {
        d: 'M9 2v2',
        key: '165o2o'
      }
    ],
    [
      'path',
      {
        d: 'M9 20v2',
        key: 'i2bqo8'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Wf = te(
  'Eye',
  [
    ['path',
    {
      d: 'M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z',
      key: 'rwhkz3'
    }
    ],
    [
      'circle',
      {
        cx: '12',
        cy: '12',
        r: '3',
        key: '1v7zrd'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Qf = te(
  'Filter',
  [
    ['polygon',
    {
      points: '22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3',
      key: '1yg77f'
    }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Kf = te(
  'HardDrive',
  [
    ['line',
    {
      x1: '22',
      x2: '2',
      y1: '12',
      y2: '12',
      key: '1y58io'
    }
    ],
    [
      'path',
      {
        d: 'M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z',
        key: 'oot6mr'
      }
    ],
    [
      'line',
      {
        x1: '6',
        x2: '6.01',
        y1: '16',
        y2: '16',
        key: 'sgf278'
      }
    ],
    [
      'line',
      {
        x1: '10',
        x2: '10.01',
        y1: '16',
        y2: '16',
        key: '1l4acy'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Gf = te(
  'LineChart',
  [
    ['path',
    {
      d: 'M3 3v18h18',
      key: '1s2lah'
    }
    ],
    [
      'path',
      {
        d: 'm19 9-5 5-4-4-3 3',
        key: '2osh9i'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const ac = te(
  'Package',
  [
    ['path',
    {
      d: 'm7.5 4.27 9 5.15',
      key: '1c824w'
    }
    ],
    [
      'path',
      {
        d: 'M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z',
        key: 'hh9hay'
      }
    ],
    [
      'path',
      {
        d: 'm3.3 7 8.7 5 8.7-5',
        key: 'g66t2b'
      }
    ],
    [
      'path',
      {
        d: 'M12 22V12',
        key: 'd0xqtd'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Yf = te(
  'Play',
  [
    ['polygon',
    {
      points: '5 3 19 12 5 21 5 3',
      key: '191637'
    }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Xf = te(
  'Search',
  [
    ['circle',
    {
      cx: '11',
      cy: '11',
      r: '8',
      key: '4ej97u'
    }
    ],
    [
      'path',
      {
        d: 'm21 21-4.3-4.3',
        key: '1qie3q'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const cc = te(
  'Server',
  [
    ['rect',
    {
      width: '20',
      height: '8',
      x: '2',
      y: '2',
      rx: '2',
      ry: '2',
      key: 'ngkwjq'
    }
    ],
    [
      'rect',
      {
        width: '20',
        height: '8',
        x: '2',
        y: '14',
        rx: '2',
        ry: '2',
        key: 'iecqi9'
      }
    ],
    [
      'line',
      {
        x1: '6',
        x2: '6.01',
        y1: '6',
        y2: '6',
        key: '16zg32'
      }
    ],
    [
      'line',
      {
        x1: '6',
        x2: '6.01',
        y1: '18',
        y2: '18',
        key: 'nzw8ys'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const dc = te(
  'Settings',
  [
    ['path',
    {
      d: 'M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z',
      key: '1qme2f'
    }
    ],
    [
      'circle',
      {
        cx: '12',
        cy: '12',
        r: '3',
        key: '1v7zrd'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Zf = te(
  'TrendingDown',
  [
    ['polyline',
    {
      points: '22 17 13.5 8.5 8.5 13.5 2 7',
      key: '1r2t7k'
    }
    ],
    [
      'polyline',
      {
        points: '16 17 22 17 22 11',
        key: '11uiuu'
      }
    ]
  ]
); /**
 * @license lucide-react v0.344.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */
const Ai = te(
  'TrendingUp',
  [
    ['polyline',
    {
      points: '22 7 13.5 15.5 8.5 10.5 2 17',
      key: '126l90'
    }
    ],
    [
      'polyline',
      {
        points: '16 7 22 7 22 13',
        key: 'kwv8wd'
      }
    ]
  ]
),
Nn = [
],
Jf = [
  {
    id: 'solver-1',
    name: 'Simple Tests',
    version: 'v0.0.1',
    description: 'Simple tests including echo meant to test framework functionality',
    status: 'active',
    totalRuns: 234,
    successRate: 97,
    avgRuntime: 143,
    lastRun: '2 hours ago',
    systems: [
      'Dev-System'
    ]
  },
],
qf = [
  {
    id: 'system-1',
    name: 'HPC-Cluster-01',
    description: 'Primary production HPC cluster for scientific computing',
    status: 'operational',
    cpu: 'Intel Xeon Platinum 8380',
    cores: 320,
    memory: '1.5 TB',
    memoryUsage: 67,
    network: '100 Gb/s InfiniBand',
    location: 'Data Center A',
    uptime: '99.8%',
    totalRuns: 487,
    solvers: [
      'LAMMPS',
      'OpenFOAM',
      'GROMACS',
      'VASP',
      'Palabos'
    ]
  },
  {
    id: 'system-2',
    name: 'HPC-Cluster-02',
    description: 'Secondary HPC cluster with GPU acceleration',
    status: 'operational',
    cpu: 'AMD EPYC 9654',
    cores: 384,
    memory: '2.0 TB',
    memoryUsage: 54,
    network: '200 Gb/s InfiniBand',
    location: 'Data Center A',
    uptime: '99.9%',
    totalRuns: 392,
    solvers: [
      'LAMMPS',
      'OpenFOAM',
      'GROMACS',
      'NAMD',
      'VASP'
    ]
  },
  {
    id: 'system-3',
    name: 'Dev-System',
    description: 'Development and testing environment',
    status: 'operational',
    cpu: 'Intel Xeon Gold 6342',
    cores: 48,
    memory: '256 GB',
    memoryUsage: 42,
    network: '25 Gb/s Ethernet',
    location: 'Lab 3B',
    uptime: '98.5%',
    totalRuns: 156,
    solvers: [
      'LAMMPS',
      'NAMD'
    ]
  }
];
function Yo() {
  const e = Nn.slice(0, 5),
  t = Nn.filter(s => s.status === 'passed').length,
  n = Nn.filter(s => s.status === 'failed').length,
  r = Nn.length,
  l = Math.round(t / r * 100),
  i = [
    {
      label: 'Total Test Runs',
      value: r.toString(),
      change: '+12%',
      trend: 'up',
      icon: uc
    },
    {
      label: 'Pass Rate',
      value: `${ l }%`,
      change: '+5%',
      trend: 'up',
      icon: Go
    },
    {
      label: 'Failed Tests',
      value: n.toString(),
      change: '-3%',
      trend: 'down',
      icon: Ko
    },
    {
      label: 'Avg Runtime',
      value: '142s',
      change: '-8%',
      trend: 'down',
      icon: Ai
    }
  ];
  return o.jsxs(
    'div',
    {
      className: 'p-8',
      children: [
        o.jsxs(
          'div',
          {
            className: 'mb-8',
            children: [
              o.jsx(
                'h1',
                {
                  className: 'text-3xl font-bold text-slate-900',
                  children: 'Dashboard'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-slate-600 mt-2',
                  children: 'Overview of regression testing platform performance'
                }
              )
            ]
          }
        ),
        o.jsx(
          'div',
          {
            className: 'grid grid-cols-4 gap-6 mb-8',
            children: i.map(
              s => {
                const u = s.icon;
                return o.jsxs(
                  'div',
                  {
                    className: 'bg-white rounded-lg p-6 border border-slate-200',
                    children: [
                      o.jsxs(
                        'div',
                        {
                          className: 'flex items-center justify-between mb-4',
                          children: [
                            o.jsx(
                              'div',
                              {
                                className: `p-3 rounded-lg ${ s.label === 'Failed Tests' ? 'bg-red-100' : 'bg-cyan-100' }`,
                                children: o.jsx(
                                  u,
                                  {
                                    className: `w-6 h-6 ${ s.label === 'Failed Tests' ? 'text-red-600' : 'text-cyan-600' }`
                                  }
                                )
                              }
                            ),
                            o.jsxs(
                              'span',
                              {
                                className: `text-sm font-medium flex items-center gap-1 ${ s.trend === 'up' ? 'text-green-600' : 'text-red-600' }`,
                                children: [
                                  s.trend === 'up' ? o.jsx(Ai, {
                                    className: 'w-4 h-4'
                                  }) : o.jsx(Zf, {
                                    className: 'w-4 h-4'
                                  }),
                                  s.change
                                ]
                              }
                            )
                          ]
                        }
                      ),
                      o.jsx(
                        'p',
                        {
                          className: 'text-2xl font-bold text-slate-900',
                          children: s.value
                        }
                      ),
                      o.jsx(
                        'p',
                        {
                          className: 'text-sm text-slate-600 mt-1',
                          children: s.label
                        }
                      )
                    ]
                  },
                  s.label
                )
              }
            )
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'grid grid-cols-2 gap-6',
            children: [
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg border border-slate-200',
                  children: [
                    o.jsx(
                      'div',
                      {
                        className: 'p-6 border-b border-slate-200',
                        children: o.jsx(
                          'h2',
                          {
                            className: 'text-lg font-semibold text-slate-900',
                            children: 'Recent Test Runs'
                          }
                        )
                      }
                    ),
                    o.jsx(
                      'div',
                      {
                        className: 'p-6',
                        children: o.jsx(
                          'div',
                          {
                            className: 'space-y-4',
                            children: e.map(
                              s => o.jsxs(
                                'div',
                                {
                                  className: 'flex items-center justify-between py-3 border-b border-slate-100 last:border-0',
                                  children: [
                                    o.jsxs(
                                      'div',
                                      {
                                        className: 'flex items-center gap-3',
                                        children: [
                                          o.jsx(
                                            'div',
                                            {
                                              className: `w-2 h-2 rounded-full ${ s.status === 'passed' ? 'bg-green-500' : s.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500' }`
                                            }
                                          ),
                                          o.jsxs(
                                            'div',
                                            {
                                              children: [
                                                o.jsx(
                                                  'p',
                                                  {
                                                    className: 'font-medium text-slate-900',
                                                    children: s.solver
                                                  }
                                                ),
                                                o.jsx('p', {
                                                  className: 'text-sm text-slate-600',
                                                  children: s.system
                                                })
                                              ]
                                            }
                                          )
                                        ]
                                      }
                                    ),
                                    o.jsxs(
                                      'div',
                                      {
                                        className: 'text-right',
                                        children: [
                                          o.jsxs(
                                            'p',
                                            {
                                              className: 'text-sm font-medium text-slate-900',
                                              children: [
                                                s.runtime,
                                                's'
                                              ]
                                            }
                                          ),
                                          o.jsx(
                                            'p',
                                            {
                                              className: 'text-xs text-slate-500',
                                              children: s.timestamp
                                            }
                                          )
                                        ]
                                      }
                                    )
                                  ]
                                },
                                s.id
                              )
                            )
                          }
                        )
                      }
                    )
                  ]
                }
              ),
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg border border-slate-200',
                  children: [
                    o.jsx(
                      'div',
                      {
                        className: 'p-6 border-b border-slate-200',
                        children: o.jsx(
                          'h2',
                          {
                            className: 'text-lg font-semibold text-slate-900',
                            children: 'System Status'
                          }
                        )
                      }
                    ),
                    o.jsx(
                      'div',
                      {
                        className: 'p-6',
                        children: o.jsx(
                          'div',
                          {
                            className: 'space-y-4',
                            children: [
                              'Dev-System'
                            ].map(
                              s => o.jsxs(
                                'div',
                                {
                                  className: 'flex items-center justify-between py-3 border-b border-slate-100 last:border-0',
                                  children: [
                                    o.jsxs(
                                      'div',
                                      {
                                        className: 'flex items-center gap-3',
                                        children: [
                                          o.jsx(Go, {
                                            className: 'w-5 h-5 text-green-500'
                                          }),
                                          o.jsx('span', {
                                            className: 'font-medium text-slate-900',
                                            children: s
                                          })
                                        ]
                                      }
                                    ),
                                    o.jsx(
                                      'span',
                                      {
                                        className: 'text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full',
                                        children: 'Operational'
                                      }
                                    )
                                  ]
                                },
                                s
                              )
                            )
                          }
                        )
                      }
                    )
                  ]
                }
              )
            ]
          }
        ),
        o.jsx(
          'div',
          {
            className: 'mt-6 bg-cyan-50 border border-cyan-200 rounded-lg p-6',
            children: o.jsxs(
              'div',
              {
                className: 'flex items-start gap-3',
                children: [
                  o.jsx(Ko, {
                    className: 'w-5 h-5 text-cyan-600 mt-0.5'
                  }),
                  o.jsxs(
                    'div',
                    {
                      children: [
                        o.jsx(
                          'h3',
                          {
                            className: 'font-semibold text-cyan-900',
                            children: 'Platform Notice'
                          }
                        ),
                        o.jsx(
                          'p',
                          {
                            className: 'text-sm text-cyan-800 mt-1',
                            children: 'All systems operational. Next scheduled maintenance: March 15, 2026. Performance metrics are being collected continuously.'
                          }
                        )
                      ]
                    }
                  )
                ]
              }
            )
          }
        )
      ]
    }
  )
}
function bf() {
  const [e,
  t] = Ue.useState(''),
  [
    n,
    r
  ] = Ue.useState('all'),
  [
    l,
    i
  ] = Ue.useState(null),
  s = Nn.filter(
    u => {
      const a = u.solver.toLowerCase().includes(e.toLowerCase()) ||
      u.system.toLowerCase().includes(e.toLowerCase()),
      d = n === 'all' ||
      u.status === n;
      return a &&
      d
    }
  );
  return o.jsxs(
    'div',
    {
      className: 'p-8',
      children: [
        o.jsxs(
          'div',
          {
            className: 'mb-8',
            children: [
              o.jsx(
                'h1',
                {
                  className: 'text-3xl font-bold text-slate-900',
                  children: 'Test Runs'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-slate-600 mt-2',
                  children: 'Complete history of regression test executions'
                }
              )
            ]
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'bg-white rounded-lg border border-slate-200',
            children: [
              o.jsx(
                'div',
                {
                  className: 'p-6 border-b border-slate-200',
                  children: o.jsxs(
                    'div',
                    {
                      className: 'flex items-center gap-4',
                      children: [
                        o.jsxs(
                          'div',
                          {
                            className: 'flex-1 relative',
                            children: [
                              o.jsx(
                                Xf,
                                {
                                  className: 'absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400'
                                }
                              ),
                              o.jsx(
                                'input',
                                {
                                  type: 'text',
                                  placeholder: 'Search by solver or system...',
                                  value: e,
                                  onChange: u => t(u.target.value),
                                  className: 'w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500'
                                }
                              )
                            ]
                          }
                        ),
                        o.jsxs(
                          'div',
                          {
                            className: 'flex items-center gap-2',
                            children: [
                              o.jsx(Qf, {
                                className: 'w-5 h-5 text-slate-600'
                              }),
                              o.jsxs(
                                'select',
                                {
                                  value: n,
                                  onChange: u => r(u.target.value),
                                  className: 'px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500',
                                  children: [
                                    o.jsx('option', {
                                      value: 'all',
                                      children: 'All Status'
                                    }),
                                    o.jsx('option', {
                                      value: 'passed',
                                      children: 'Passed'
                                    }),
                                    o.jsx('option', {
                                      value: 'failed',
                                      children: 'Failed'
                                    }),
                                    o.jsx('option', {
                                      value: 'running',
                                      children: 'Running'
                                    })
                                  ]
                                }
                              )
                            ]
                          }
                        )
                      ]
                    }
                  )
                }
              ),
              o.jsx(
                'div',
                {
                  className: 'overflow-x-auto',
                  children: o.jsxs(
                    'table',
                    {
                      id: 'test-run-table',
                      className: 'w-full',
                      children: [
                        o.jsx(
                          'thead',
                          {
                            className: 'bg-slate-50 border-b border-slate-200',
                            children: o.jsxs(
                              'tr',
                              {
                                children: [
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'Run ID'
                                    }
                                  ),
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'Solver'
                                    }
                                  ),
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'System'
                                    }
                                  ),
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'Status'
                                    }
                                  ),
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'Runtime'
                                    }
                                  ),
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'Timestamp'
                                    }
                                  ),
                                  o.jsx(
                                    'th',
                                    {
                                      className: 'px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase',
                                      children: 'Actions'
                                    }
                                  )
                                ]
                              }
                            )
                          }
                        ),
                        o.jsx(
                          'tbody',
                          {
                            className: 'divide-y divide-slate-200',
                            id: "test-run-table-body",
                            children: s.map(
                              u => o.jsxs(
                                'tr',
                                {
                                  className: 'hover:bg-slate-50',
                                  children: [
                                    o.jsx(
                                      'td',
                                      {
                                        className: 'px-6 py-4 text-sm text-slate-900 font-mono',
                                        children: u.id
                                      }
                                    ),
                                    o.jsx(
                                      'td',
                                      {
                                        className: 'px-6 py-4 text-sm font-medium text-slate-900',
                                        children: u.solver
                                      }
                                    ),
                                    o.jsx(
                                      'td',
                                      {
                                        className: 'px-6 py-4 text-sm text-slate-600',
                                        children: u.system
                                      }
                                    ),
                                    o.jsx(
                                      'td',
                                      {
                                        className: 'px-6 py-4',
                                        children: o.jsx(
                                          'span',
                                          {
                                            className: `inline-flex px-3 py-1 text-xs font-medium rounded-full ${ u.status === 'passed' ? 'bg-green-100 text-green-700' : u.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700' }`,
                                            children: u.status
                                          }
                                        )
                                      }
                                    ),
                                    o.jsxs(
                                      'td',
                                      {
                                        className: 'px-6 py-4 text-sm text-slate-900',
                                        children: [
                                          u.runtime,
                                          's'
                                        ]
                                      }
                                    ),
                                    o.jsx(
                                      'td',
                                      {
                                        className: 'px-6 py-4 text-sm text-slate-600',
                                        children: u.timestamp
                                      }
                                    ),
                                    o.jsx(
                                      'td',
                                      {
                                        className: 'px-6 py-4',
                                        children: o.jsxs(
                                          'button',
                                          {
                                            onClick: () => i(u),
                                            className: 'text-cyan-600 hover:text-cyan-700 flex items-center gap-1',
                                            children: [
                                              o.jsx(Wf, {
                                                className: 'w-4 h-4'
                                              }),
                                              o.jsx('span', {
                                                className: 'text-sm',
                                                children: 'View'
                                              })
                                            ]
                                          }
                                        )
                                      }
                                    )
                                  ]
                                },
                                u.id
                              )
                            )
                          }
                        )
                      ]
                    }
                  )
                }
              )
            ]
          }
        ),
        l &&
        o.jsx(
          'div',
          {
            className: 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50',
            children: o.jsxs(
              'div',
              {
                className: 'bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto',
                children: [
                  o.jsxs(
                    'div',
                    {
                      className: 'p-6 border-b border-slate-200',
                      children: [
                        o.jsx(
                          'h2',
                          {
                            className: 'text-xl font-semibold text-slate-900',
                            children: 'Test Run Details'
                          }
                        ),
                        o.jsxs(
                          'p',
                          {
                            className: 'text-sm text-slate-600 mt-1',
                            children: [
                              'Run ID: ',
                              l.id
                            ]
                          }
                        )
                      ]
                    }
                  ),
                  o.jsxs(
                    'div',
                    {
                      className: 'p-6 space-y-4',
                      children: [
                        o.jsxs(
                          'div',
                          {
                            className: 'mt-6',
                            children: [
                              o.jsx(
                                'p',
                                {
                                  className: 'text-sm font-medium text-slate-600 mb-2',
                                  children: 'Log Output'
                                }
                              ),
                              o.jsxs(
                                'div',
                                {
                                  className: 'bg-slate-900 text-green-400 rounded-lg p-4 font-mono text-xs max-h-48 overflow-auto',
                                  children: [
                                    o.jsx('div', {
                                      children: 'Starting solver execution...'
                                    }),
                                  ]
                                }
                              )
                            ]
                          }
                        )
                      ]
                    }
                  ),
                  o.jsx(
                    'div',
                    {
                      className: 'p-6 border-t border-slate-200',
                      children: o.jsx(
                        'button',
                        {
                          onClick: () => i(null),
                          className: 'w-full px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800',
                          children: 'Close'
                        }
                      )
                    }
                  )
                ]
              }
            )
          }
        )
      ]
    }
  )
}
function ep() {
  return o.jsxs(
    'div',
    {
      className: 'p-8',
      children: [
        o.jsxs(
          'div',
          {
            className: 'mb-8',
            children: [
              o.jsx(
                'h1',
                {
                  className: 'text-3xl font-bold text-slate-900',
                  children: 'Solvers'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-slate-600 mt-2',
                  children: 'Configured scientific solvers for regression testing'
                }
              )
            ]
          }
        ),
        o.jsx(
          'div',
          {
            className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
            children: Jf.map(
              e => o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg border border-slate-200 hover:shadow-lg transition-shadow',
                  children: [
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6 border-b border-slate-200',
                        children: [
                          o.jsxs(
                            'div',
                            {
                              className: 'flex items-start justify-between mb-4',
                              children: [
                                o.jsxs(
                                  'div',
                                  {
                                    className: 'flex items-center gap-3',
                                    children: [
                                      o.jsx(
                                        'div',
                                        {
                                          className: 'p-3 bg-cyan-100 rounded-lg',
                                          children: o.jsx(ac, {
                                            className: 'w-6 h-6 text-cyan-600'
                                          })
                                        }
                                      ),
                                      o.jsxs(
                                        'div',
                                        {
                                          children: [
                                            o.jsx(
                                              'h3',
                                              {
                                                className: 'font-semibold text-slate-900',
                                                children: e.name
                                              }
                                            ),
                                            o.jsx('p', {
                                              className: 'text-xs text-slate-600',
                                              children: e.version
                                            })
                                          ]
                                        }
                                      )
                                    ]
                                  }
                                ),
                                o.jsx(
                                  'span',
                                  {
                                    className: `px-2 py-1 text-xs font-medium rounded ${ e.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700' }`,
                                    children: e.status
                                  }
                                )
                              ]
                            }
                          ),
                          o.jsx(
                            'p',
                            {
                              className: 'text-sm text-slate-600',
                              children: e.description
                            }
                          )
                        ]
                      }
                    ),
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6',
                        children: [
                          o.jsxs(
                            'div',
                            {
                              className: 'mb-4',
                              children: [
                                o.jsx(
                                  'p',
                                  {
                                    className: 'text-xs text-slate-600 mb-2',
                                    children: 'Compatible Systems'
                                  }
                                ),
                                o.jsx(
                                  'div',
                                  {
                                    className: 'flex flex-wrap gap-2',
                                    children: e.systems.map(
                                      t => o.jsx(
                                        'span',
                                        {
                                          className: 'px-2 py-1 text-xs bg-slate-100 text-slate-700 rounded',
                                          children: t
                                        },
                                        t
                                      )
                                    )
                                  }
                                )
                              ]
                            }
                          ),
                          o.jsxs(
                            'div',
                            {
                              className: 'flex gap-2',
                              children: [
                                o.jsxs(
                                  'button',
                                  {
                                    id: 'run-button',
                                    onClick: runMainTestRunner,
                                    className: 'flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700',
                                    children: [
                                      o.jsx(Yf, {
                                        className: 'w-4 h-4'
                                      }),
                                      'Run Test'
                                    ]
                                  }
                                ),
                              ]
                            }
                          )
                        ]
                      }
                    )
                  ]
                },
                e.id
              )
            )
          }
        ),
      ]
    }
  )
}
const runMainTestRunner = async () => {

      const response = await fetch("/api/run_tests");
      const data = await response.json();

//  {
//    id: 'RUN-001234',
//    solver: 'LAMMPS',
//    system: 'HPC-Cluster-01',
//    status: 'passed',
//    runtime: 145,
//    mlups: '2.8M',
//    timestamp: '2026-02-04 10:23:15'
//  },

      for (let i = 0; i < data.length; i++) {
        let id = data[i]["name"];
        let solver = "Dev Tests";
        let system = "Dev-System";
        let status = "passed";
        if (data[i]["returncode"] == 0) {
            status = "passed";
        } else {
            status = "failed";
        }
        let runtime = data[i]["runtime"]
        let timestamp = data[i]["timestamp"]
        setTimeout(() => {document.getElementById("button-test-runs").click()}, 300);

        setTimeout(() => {
            const newRow = document.createElement('tr');
            newRow.innerHTML =
            `
                <td class = "px-6 py-4 text-sm text-slate-900 font-mono"> ${id} </td>
                <td class = "px-6 py-4 text-sm text-slate-900 font-mono"> ${solver} </td>
                <td class = "px-6 py-4 text-sm text-slate-900 font-mono"> ${system} </td>
                <td class = "px-6 py-4"> <span class = "inline-flex px-3 py-1 text-xs font-medium rounded-full ${ status === 'passed' ? 'bg-green-100 text-green-700' : status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700' }"
> ${status} </span> </td>
                <td class = "px-6 py-4 text-sm text-slate-900 font-mono"> ${runtime}s </td>
                <td class = "px-6 py-4 text-sm text-slate-900 font-mono"> ${timestamp} </td>
                <td class="px-6 py-4">
                <button id="view_${id}" class="text-cyan-600 hover:text-cyan-700 flex items-center gap-1" data-full-info=${data[i].stdout}>
                    <svg class="w-4 h-4"><!-- icon here --></svg>
                    <span class="text-sm">View</span>
                </button>
                </td>
            `
            ;
            const button = newRow.querySelector(`#view_${id}`);
            button.addEventListener('click', (e) => {
                const info = e.currentTarget.getAttribute('data-full-info');
                console.log('Output', info);
                alert(`output: ${info}`);
            });           const testRunTableBody = document.getElementById('test-run-table-body');
            testRunTableBody.appendChild(newRow);
        }, 300);
      }
      console.log(data);
}
function tp() {
  return o.jsxs(
    'div',
    {
      className: 'p-8',
      children: [
        o.jsxs(
          'div',
          {
            className: 'mb-8',
            children: [
              o.jsx(
                'h1',
                {
                  className: 'text-3xl font-bold text-slate-900',
                  children: 'Systems & Resources'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-slate-600 mt-2',
                  children: 'HPC systems and compute resources available for testing'
                }
              )
            ]
          }
        ),
        o.jsx(
          'div',
          {
            className: 'grid grid-cols-1 gap-6',
            children: qf.map(
              e => o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg border border-slate-200',
                  children: [
                    o.jsx(
                      'div',
                      {
                        className: 'p-6 border-b border-slate-200',
                        children: o.jsxs(
                          'div',
                          {
                            className: 'flex items-center justify-between',
                            children: [
                              o.jsxs(
                                'div',
                                {
                                  className: 'flex items-center gap-4',
                                  children: [
                                    o.jsx(
                                      'div',
                                      {
                                        className: 'p-3 bg-cyan-100 rounded-lg',
                                        children: o.jsx(cc, {
                                          className: 'w-6 h-6 text-cyan-600'
                                        })
                                      }
                                    ),
                                    o.jsxs(
                                      'div',
                                      {
                                        children: [
                                          o.jsx(
                                            'h3',
                                            {
                                              className: 'text-xl font-semibold text-slate-900',
                                              children: e.name
                                            }
                                          ),
                                          o.jsx(
                                            'p',
                                            {
                                              className: 'text-sm text-slate-600',
                                              children: e.description
                                            }
                                          )
                                        ]
                                      }
                                    )
                                  ]
                                }
                              ),
                              o.jsx(
                                'span',
                                {
                                  className: `px-3 py-1 text-sm font-medium rounded-full ${ e.status === 'operational' ? 'bg-green-100 text-green-700' : e.status === 'maintenance' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700' }`,
                                  children: e.status
                                }
                              )
                            ]
                          }
                        )
                      }
                    ),
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6',
                        children: [
                          o.jsxs(
                            'div',
                            {
                              className: 'grid grid-cols-4 gap-6',
                              children: [
                                o.jsxs(
                                  'div',
                                  {
                                    children: [
                                      o.jsxs(
                                        'div',
                                        {
                                          className: 'flex items-center gap-2 mb-2',
                                          children: [
                                            o.jsx(Bf, {
                                              className: 'w-4 h-4 text-slate-600'
                                            }),
                                            o.jsx(
                                              'span',
                                              {
                                                className: 'text-sm font-medium text-slate-600',
                                                children: 'CPU'
                                              }
                                            )
                                          ]
                                        }
                                      ),
                                      o.jsx(
                                        'p',
                                        {
                                          className: 'text-lg font-semibold text-slate-900',
                                          children: e.cpu
                                        }
                                      ),
                                      o.jsxs(
                                        'p',
                                        {
                                          className: 'text-xs text-slate-600 mt-1',
                                          children: [
                                            e.cores,
                                            ' cores'
                                          ]
                                        }
                                      )
                                    ]
                                  }
                                ),
                                o.jsxs(
                                  'div',
                                  {
                                    children: [
                                      o.jsxs(
                                        'div',
                                        {
                                          className: 'flex items-center gap-2 mb-2',
                                          children: [
                                            o.jsx(Kf, {
                                              className: 'w-4 h-4 text-slate-600'
                                            }),
                                            o.jsx(
                                              'span',
                                              {
                                                className: 'text-sm font-medium text-slate-600',
                                                children: 'Memory'
                                              }
                                            )
                                          ]
                                        }
                                      ),
                                      o.jsx(
                                        'p',
                                        {
                                          className: 'text-lg font-semibold text-slate-900',
                                          children: e.memory
                                        }
                                      ),
                                      o.jsx(
                                        'div',
                                        {
                                          className: 'w-full bg-slate-200 rounded-full h-1.5 mt-2',
                                          children: o.jsx(
                                            'div',
                                            {
                                              className: 'bg-cyan-600 h-1.5 rounded-full',
                                              style: {
                                                width: `${ e.memoryUsage }%`
                                              }
                                            }
                                          )
                                        }
                                      ),
                                      o.jsxs(
                                        'p',
                                        {
                                          className: 'text-xs text-slate-600 mt-1',
                                          children: [
                                            e.memoryUsage,
                                            '% used'
                                          ]
                                        }
                                      )
                                    ]
                                  }
                                ),
                                o.jsxs(
                                  'div',
                                  {
                                    children: [
                                      o.jsxs(
                                        'div',
                                        {
                                          className: 'flex items-center gap-2 mb-2',
                                          children: [
                                            o.jsx(Os, {
                                              className: 'w-4 h-4 text-slate-600'
                                            }),
                                            o.jsx(
                                              'span',
                                              {
                                                className: 'text-sm font-medium text-slate-600',
                                                children: 'Network'
                                              }
                                            )
                                          ]
                                        }
                                      ),
                                      o.jsx(
                                        'p',
                                        {
                                          className: 'text-lg font-semibold text-slate-900',
                                          children: e.network
                                        }
                                      )
                                    ]
                                  }
                                ),
                                o.jsxs(
                                  'div',
                                  {
                                    children: [
                                      o.jsx(
                                        'div',
                                        {
                                          className: 'flex items-center gap-2 mb-2',
                                          children: o.jsx(
                                            'span',
                                            {
                                              className: 'text-sm font-medium text-slate-600',
                                              children: 'Location'
                                            }
                                          )
                                        }
                                      ),
                                      o.jsx(
                                        'p',
                                        {
                                          className: 'text-lg font-semibold text-slate-900',
                                          children: e.location
                                        }
                                      ),
                                      o.jsxs(
                                        'p',
                                        {
                                          className: 'text-xs text-slate-600 mt-1',
                                          children: [
                                            'Uptime: ',
                                            e.uptime
                                          ]
                                        }
                                      )
                                    ]
                                  }
                                )
                              ]
                            }
                          ),
                          o.jsx(
                            'div',
                            {
                              className: 'mt-6 pt-6 border-t border-slate-200',
                              children: o.jsxs(
                                'div',
                                {
                                  className: 'flex items-center justify-between',
                                  children: [
                                    o.jsxs(
                                      'div',
                                      {
                                        children: [
                                          o.jsx(
                                            'p',
                                            {
                                              className: 'text-sm text-slate-600',
                                              children: 'Compatible Solvers'
                                            }
                                          ),
                                          o.jsx(
                                            'div',
                                            {
                                              className: 'flex gap-2 mt-2',
                                              children: e.solvers.map(
                                                t => o.jsx(
                                                  'span',
                                                  {
                                                    className: 'px-2 py-1 text-xs bg-cyan-50 text-cyan-700 rounded',
                                                    children: t
                                                  },
                                                  t
                                                )
                                              )
                                            }
                                          )
                                        ]
                                      }
                                    ),
                                    o.jsxs(
                                      'div',
                                      {
                                        className: 'text-right',
                                        children: [
                                          o.jsx(
                                            'p',
                                            {
                                              className: 'text-sm text-slate-600',
                                              children: 'Total Test Runs'
                                            }
                                          ),
                                          o.jsx(
                                            'p',
                                            {
                                              className: 'text-2xl font-bold text-slate-900 mt-1',
                                              children: e.totalRuns
                                            }
                                          )
                                        ]
                                      }
                                    )
                                  ]
                                }
                              )
                            }
                          )
                        ]
                      }
                    )
                  ]
                },
                e.id
              )
            )
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'mt-8 bg-white rounded-lg border border-slate-200 p-6',
            children: [
              o.jsx(
                'h2',
                {
                  className: 'text-lg font-semibold text-slate-900 mb-4',
                  children: 'Resource Management'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-slate-600 mb-4',
                  children: 'Systems define the compute environments where tests are executed. The platform is execution-agnostic and does not depend on specific schedulers or cluster configurations. Solver scripts define their own run logic while the system provides standardized logging and metric extraction.'
                }
              ),
              o.jsx(
                'button',
                {
                  className: 'px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800',
                  children: 'Add New System'
                }
              )
            ]
          }
        )
      ]
    }
  )
}
function np() {
  return o.jsxs(
    'div',
    {
      className: 'p-8',
      children: [
        o.jsxs(
          'div',
          {
            className: 'mb-8',
            children: [
              o.jsx(
                'h1',
                {
                  className: 'text-3xl font-bold text-slate-900',
                  children: 'Performance Trends'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-slate-600 mt-2',
                  children: 'Historical performance metrics and anomaly detection'
                }
              )
            ]
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'grid grid-cols-3 gap-6 mb-8',
            children: [
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg p-6 border border-slate-200',
                  children: [
                    o.jsxs(
                      'div',
                      {
                        className: 'flex items-center gap-3 mb-4',
                        children: [
                          o.jsx(
                            'div',
                            {
                              className: 'p-3 bg-cyan-100 rounded-lg',
                              children: o.jsx(Ai, {
                                className: 'w-6 h-6 text-cyan-600'
                              })
                            }
                          ),
                          o.jsxs(
                            'div',
                            {
                              children: [
                                o.jsx(
                                  'p',
                                  {
                                    className: 'text-2xl font-bold text-slate-900',
                                    children: '+12%'
                                  }
                                ),
                                o.jsx(
                                  'p',
                                  {
                                    className: 'text-sm text-slate-600',
                                    children: 'Performance Gain'
                                  }
                                )
                              ]
                            }
                          )
                        ]
                      }
                    ),
                    o.jsx(
                      'p',
                      {
                        className: 'text-xs text-slate-500',
                        children: 'vs. last week'
                      }
                    )
                  ]
                }
              ),
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg p-6 border border-slate-200',
                  children: [
                    o.jsxs(
                      'div',
                      {
                        className: 'flex items-center gap-3 mb-4',
                        children: [
                          o.jsx(
                            'div',
                            {
                              className: 'p-3 bg-green-100 rounded-lg',
                              children: o.jsx(Os, {
                                className: 'w-6 h-6 text-green-600'
                              })
                            }
                          ),
                          o.jsxs(
                            'div',
                            {
                              children: [
                                o.jsx(
                                  'p',
                                  {
                                    className: 'text-2xl font-bold text-slate-900',
                                    children: '142s'
                                  }
                                ),
                                o.jsx(
                                  'p',
                                  {
                                    className: 'text-sm text-slate-600',
                                    children: 'Avg Runtime'
                                  }
                                )
                              ]
                            }
                          )
                        ]
                      }
                    ),
                    o.jsx(
                      'p',
                      {
                        className: 'text-xs text-slate-500',
                        children: '8% faster than baseline'
                      }
                    )
                  ]
                }
              ),
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg p-6 border border-slate-200',
                  children: [
                    o.jsxs(
                      'div',
                      {
                        className: 'flex items-center gap-3 mb-4',
                        children: [
                          o.jsx(
                            'div',
                            {
                              className: 'p-3 bg-blue-100 rounded-lg',
                              children: o.jsx(Gf, {
                                className: 'w-6 h-6 text-blue-600'
                              })
                            }
                          ),
                          o.jsxs(
                            'div',
                            {
                              children: [
                                o.jsx(
                                  'p',
                                  {
                                    className: 'text-sm text-slate-600',
                                    children: 'Avg MLUPS'
                                  }
                                )
                              ]
                            }
                          )
                        ]
                      }
                    ),
                    o.jsx(
                      'p',
                      {
                        className: 'text-xs text-slate-500',
                        children: 'Stable performance'
                      }
                    )
                  ]
                }
              )
            ]
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'bg-white rounded-lg border border-slate-200 mb-6',
            children: [
              o.jsxs(
                'div',
                {
                  className: 'p-6 border-b border-slate-200',
                  children: [
                    o.jsx(
                      'h2',
                      {
                        className: 'text-lg font-semibold text-slate-900',
                        children: 'Runtime Performance (Last 30 Days)'
                      }
                    ),
                    o.jsx(
                      'p',
                      {
                        className: 'text-sm text-slate-600 mt-1',
                        children: 'Time-to-solution trends across all solvers'
                      }
                    )
                  ]
                }
              ),
              o.jsxs(
                'div',
                {
                  className: 'p-6',
                  children: [
                    o.jsx(
                      'div',
                      {
                        className: 'h-64 flex items-end justify-between gap-2',
                        children: [
                          145,
                          138,
                          152,
                          142,
                          135,
                          140,
                          138,
                          145,
                          141,
                          139,
                          136,
                          142,
                          138,
                          144,
                          140,
                          137,
                          142,
                          139,
                          143,
                          138,
                          140,
                          141,
                          137,
                          139,
                          142,
                          138,
                          136,
                          140,
                          138,
                          142
                        ].map(
                          (e, t) => {
                            const n = e / 152 * 100;
                            return o.jsx(
                              'div',
                              {
                                className: 'flex-1 bg-cyan-500 hover:bg-cyan-600 rounded-t transition-colors',
                                style: {
                                  height: `${ n }%`
                                },
                                title: `${ e }s`
                              },
                              t
                            )
                          }
                        )
                      }
                    ),
                    o.jsxs(
                      'div',
                      {
                        className: 'flex justify-between mt-4 text-xs text-slate-600',
                        children: [
                          o.jsx('span', {
                            children: '30 days ago'
                          }),
                          o.jsx('span', {
                            children: 'Today'
                          })
                        ]
                      }
                    )
                  ]
                }
              )
            ]
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'grid grid-cols-2 gap-6',
            children: [
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg border border-slate-200',
                  children: [
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6 border-b border-slate-200',
                        children: [
                          o.jsx(
                            'h2',
                            {
                              className: 'text-lg font-semibold text-slate-900',
                              children: 'MLUPS Performance'
                            }
                          ),
                          o.jsx(
                            'p',
                            {
                              className: 'text-sm text-slate-600 mt-1',
                              children: 'Solver throughput over time'
                            }
                          )
                        ]
                      }
                    ),
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6',
                        children: [
                          o.jsx(
                            'div',
                            {
                              className: 'h-48 flex items-end justify-between gap-2',
                              children: [
                                2.4,
                                2.5,
                                2.6,
                                2.7,
                                2.8,
                                2.7,
                                2.9,
                                2.8,
                                2.9,
                                2.8,
                                2.9,
                                3,
                                2.9,
                                2.8,
                                2.9
                              ].map(
                                (e, t) => {
                                  const n = e / 3 * 100;
                                  return o.jsx(
                                    'div',
                                    {
                                      className: 'flex-1 bg-green-500 hover:bg-green-600 rounded-t transition-colors',
                                      style: {
                                        height: `${ n }%`
                                      },
                                      title: `${ e }M`
                                    },
                                    t
                                  )
                                }
                              )
                            }
                          ),
                          o.jsxs(
                            'div',
                            {
                              className: 'flex justify-between mt-4 text-xs text-slate-600',
                              children: [
                                o.jsx('span', {
                                  children: '2 weeks ago'
                                }),
                                o.jsx('span', {
                                  children: 'Today'
                                })
                              ]
                            }
                          )
                        ]
                      }
                    )
                  ]
                }
              ),
              o.jsxs(
                'div',
                {
                  className: 'bg-white rounded-lg border border-slate-200',
                  children: [
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6 border-b border-slate-200',
                        children: [
                          o.jsx(
                            'h2',
                            {
                              className: 'text-lg font-semibold text-slate-900',
                              children: 'Test Success Rate'
                            }
                          ),
                          o.jsx(
                            'p',
                            {
                              className: 'text-sm text-slate-600 mt-1',
                              children: 'Pass/fail ratio trends'
                            }
                          )
                        ]
                      }
                    ),
                    o.jsxs(
                      'div',
                      {
                        className: 'p-6',
                        children: [
                          o.jsx(
                            'div',
                            {
                              className: 'h-48 flex items-end justify-between gap-2',
                              children: [
                                92,
                                94,
                                93,
                                95,
                                96,
                                94,
                                95,
                                97,
                                96,
                                95,
                                96,
                                97,
                                96,
                                98,
                                97
                              ].map(
                                (e, t) => {
                                  const n = e / 100 * 100;
                                  return o.jsx(
                                    'div',
                                    {
                                      className: 'flex-1 bg-blue-500 hover:bg-blue-600 rounded-t transition-colors',
                                      style: {
                                        height: `${ n }%`
                                      },
                                      title: `${ e }%`
                                    },
                                    t
                                  )
                                }
                              )
                            }
                          ),
                          o.jsxs(
                            'div',
                            {
                              className: 'flex justify-between mt-4 text-xs text-slate-600',
                              children: [
                                o.jsx('span', {
                                  children: '2 weeks ago'
                                }),
                                o.jsx('span', {
                                  children: 'Today'
                                })
                              ]
                            }
                          )
                        ]
                      }
                    )
                  ]
                }
              )
            ]
          }
        ),
        o.jsxs(
          'div',
          {
            className: 'mt-6 bg-amber-50 border border-amber-200 rounded-lg p-6',
            children: [
              o.jsx(
                'h3',
                {
                  className: 'font-semibold text-amber-900 mb-2',
                  children: 'Anomaly Detection'
                }
              ),
              o.jsx(
                'p',
                {
                  className: 'text-sm text-amber-800',
                  children: 'No performance anomalies detected in the last 30 days. All solvers are performing within expected ranges.'
                }
              )
            ]
          }
        )
      ]
    }
  )
}
function rp() {
  const [e,
  t] = Ue.useState('solvers'),
  n = [
    {
      id: 'solvers',
      label: 'Solvers',
      icon: ac
    },
    {
      id: 'test-runs',
      label: 'Test Runs',
      icon: uc
    },
  ],
  r = () => {
    switch (e) {
      case 'dashboard':
        return o.jsx(Yo, {
        });
      case 'test-runs':
        return o.jsx(bf, {
        });
      case 'solvers':
        return o.jsx(ep, {
        });
      case 'systems':
        return o.jsx(tp, {
        });
      case 'trends':
        return o.jsx(np, {
        });
      default:
        return o.jsx(Yo, {
        })
    }
  };
  return o.jsxs(
    'div',
    {
      className: 'min-h-screen bg-slate-50 flex',
      children: [
        o.jsxs(
          'aside',
          {
            className: 'w-64 bg-slate-900 text-white flex flex-col',
            children: [
              o.jsx(
                'div',
                {
                  className: 'p-6 border-b border-slate-700',
                  children: o.jsxs(
                    'div',
                    {
                      className: 'flex items-center gap-3',
                      children: [
                        o.jsx(dc, {
                          className: 'w-8 h-8 text-cyan-400'
                        }),
                        o.jsxs(
                          'div',
                          {
                            children: [
                              o.jsx(
                                'h1',
                                {
                                  className: 'text-lg font-semibold',
                                  children: 'HPC Testing'
                                }
                              ),
                              o.jsx(
                                'p',
                                {
                                  className: 'text-xs text-slate-400',
                                  children: 'Regression Platform'
                                }
                              )
                            ]
                          }
                        )
                      ]
                    }
                  )
                }
              ),
              o.jsx(
                'nav',
                {
                  className: 'flex-1 p-4 space-y-1',
                  children: n.map(
                    l => {
                      const i = l.icon;
                      return o.jsxs(
                        'button',
                        {
                          onClick: () => t(l.id),
                          id: `button-${l.id}`,
                          className: `w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${ e === l.id ? 'bg-cyan-600 text-white' : 'text-slate-300 hover:bg-slate-800' }`,
                          children: [
                            o.jsx(i, {
                              className: 'w-5 h-5'
                            }),
                            o.jsx('span', {
                              className: 'font-medium',
                              children: l.label
                            })
                          ]
                        },
                        l.id
                      )
                    }
                  )
                }
              ),
              o.jsx(
                'div',
                {
                  className: 'p-4 border-t border-slate-700',
                  children: o.jsxs(
                    'div',
                    {
                      className: 'text-xs text-slate-400',
                      children: [
                        o.jsx('p', {
                          children: 'Team DOW-1-26'
                        }),
                        o.jsx('p', {
                          className: 'mt-1',
                          children: 'v1.0 - February 2026'
                        })
                      ]
                    }
                  )
                }
              )
            ]
          }
        ),
        o.jsx('main', {
          className: 'flex-1 overflow-auto',
          children: r()
        })
      ]
    }
  )
}
oc(document.getElementById('root')).render(o.jsx(Ue.StrictMode, {
  children: o.jsx(rp, {
  })
}));
