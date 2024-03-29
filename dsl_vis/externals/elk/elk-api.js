(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.ELK = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/*******************************************************************************
 * Copyright (c) 2017 Kiel University and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *******************************************************************************/
var ELK = function () {
  function ELK() {
    var _this = this;

    var _ref = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {},
        _ref$defaultLayoutOpt = _ref.defaultLayoutOptions,
        defaultLayoutOptions = _ref$defaultLayoutOpt === undefined ? {} : _ref$defaultLayoutOpt,
        _ref$algorithms = _ref.algorithms,
        algorithms = _ref$algorithms === undefined ? ['layered', 'stress', 'mrtree', 'radial', 'force', 'disco'] : _ref$algorithms,
        workerFactory = _ref.workerFactory,
        workerUrl = _ref.workerUrl;

    _classCallCheck(this, ELK);

    this.defaultLayoutOptions = defaultLayoutOptions;
    this.initialized = false;

    // check valid worker construction possible
    if (typeof workerUrl === 'undefined' && typeof workerFactory === 'undefined') {
      throw new Error("Cannot construct an ELK without both 'workerUrl' and 'workerFactory'.");
    }
    var factory = workerFactory;
    if (typeof workerUrl !== 'undefined' && typeof workerFactory === 'undefined') {
      // use default Web Worker
      factory = function factory(url) {
        return new Worker(url);
      };
    }

    // create the worker
    var worker = factory(workerUrl);
    if (typeof worker.postMessage !== 'function') {
      throw new TypeError("Created worker does not provide" + " the required 'postMessage' function.");
    }

    // wrap the worker to return promises
    this.worker = new PromisedWorker(worker);

    // initially register algorithms
    this.worker.postMessage({
      cmd: 'register',
      algorithms: algorithms
    }).then(function (r) {
      return _this.initialized = true;
    }).catch(console.err);
  }

  _createClass(ELK, [{
    key: 'layout',
    value: function layout(graph) {
      var _ref2 = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {},
          _ref2$layoutOptions = _ref2.layoutOptions,
          layoutOptions = _ref2$layoutOptions === undefined ? this.defaultLayoutOptions : _ref2$layoutOptions;

      if (!graph) {
        return Promise.reject(new Error("Missing mandatory parameter 'graph'."));
      }
      return this.worker.postMessage({
        cmd: 'layout',
        graph: graph,
        options: layoutOptions
      });
    }
  }, {
    key: 'knownLayoutAlgorithms',
    value: function knownLayoutAlgorithms() {
      return this.worker.postMessage({ cmd: 'algorithms' });
    }
  }, {
    key: 'knownLayoutOptions',
    value: function knownLayoutOptions() {
      return this.worker.postMessage({ cmd: 'options' });
    }
  }, {
    key: 'knownLayoutCategories',
    value: function knownLayoutCategories() {
      return this.worker.postMessage({ cmd: 'categories' });
    }
  }, {
    key: 'terminateWorker',
    value: function terminateWorker() {
      this.worker.terminate();
    }
  }]);

  return ELK;
}();

exports.default = ELK;

var PromisedWorker = function () {
  function PromisedWorker(worker) {
    var _this2 = this;

    _classCallCheck(this, PromisedWorker);

    if (worker === undefined) {
      throw new Error("Missing mandatory parameter 'worker'.");
    }
    this.resolvers = {};
    this.worker = worker;
    this.worker.onmessage = function (answer) {
      // why is this necessary?
      setTimeout(function () {
        _this2.receive(_this2, answer);
      }, 0);
    };
  }

  _createClass(PromisedWorker, [{
    key: 'postMessage',
    value: function postMessage(msg) {
      var id = this.id || 0;
      this.id = id + 1;
      msg.id = id;
      var self = this;
      return new Promise(function (resolve, reject) {
        // prepare the resolver
        self.resolvers[id] = function (err, res) {
          if (err) {
            reject(err);
          } else {
            resolve(res);
          }
        };
        // post the message
        self.worker.postMessage(msg);
      });
    }
  }, {
    key: 'receive',
    value: function receive(self, answer) {
      var json = answer.data;
      var resolver = self.resolvers[json.id];
      if (resolver) {
        delete self.resolvers[json.id];
        if (json.error) {
          resolver(json.error);
        } else {
          resolver(null, json.data);
        }
      }
    }
  }, {
    key: 'terminate',
    value: function terminate() {
      if (this.worker.terminate) {
        this.worker.terminate();
      }
    }
  }]);

  return PromisedWorker;
}();
},{}],2:[function(require,module,exports){
"use strict";

var ELK = require('./elk-api.js').default;

Object.defineProperty(module.exports, "__esModule", {
  value: true
});
module.exports = ELK;
ELK.default = ELK;
},{"./elk-api.js":1}]},{},[2])(2)
});