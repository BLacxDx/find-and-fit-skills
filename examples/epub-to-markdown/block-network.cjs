// Application-level guard, not an OS firewall or a security audit.
const deny = () => { throw new Error('Network disabled during conversion'); };
require('node:net').Socket.prototype.connect = deny;
require('node:tls').connect = deny;
require('node:http').request = deny;
require('node:http').get = deny;
require('node:https').request = deny;
require('node:https').get = deny;
globalThis.fetch = deny;
