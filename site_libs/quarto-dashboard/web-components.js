"use strict";/*! bslib 0.5.1.9000 | (c) 2012-2023 RStudio, PBC. | License: MIT + file LICENSE */(()=>{var ae=Object.defineProperty,He=Object.defineProperties,ze=Object.getOwnPropertyDescriptor,Le=Object.getOwnPropertyDescriptors,le=Object.getOwnPropertySymbols,Ne=Object.prototype.hasOwnProperty,Me=Object.prototype.propertyIsEnumerable,he=(e,t,i)=>t in e?ae(e,t,{enumerable:!0,configurable:!0,writable:!0,value:i}):e[t]=i,V=(e,t)=>{for(var i in t||(t={}))Ne.call(t,i)&&he(e,i,t[i]);if(le)for(var i of le(t))Me.call(t,i)&&he(e,i,t[i]);return e},Ue=(e,t)=>He(e,Le(t)),k=(e,t,i,s)=>{for(var r=s>1?void 0:s?ze(t,i):t,a=e.length-1,n;a>=0;a--)(n=e[a])&&(r=(s?n(t,i,r):n(r))||r);return s&&r&&ae(t,i,r),r},Ie=(e,t,i)=>new Promise((s,r)=>{var a=o=>{try{l(i.next(o))}catch(d){r(d)}},n=o=>{try{l(i.throw(o))}catch(d){r(d)}},l=o=>o.done?s(o.value):Promise.resolve(o.value).then(a,n);l((i=i.apply(e,t)).next())}),Re=(e,t)=>t.kind==="method"&&t.descriptor&&!("value"in t.descriptor)?Ue(V({},t),{finisher(i){i.createProperty(t.key,e)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:t.key,initializer(){typeof t.initializer=="function"&&(this[t.key]=t.initializer.call(this))},finisher(i){i.createProperty(t.key,e)}},Be=(e,t,i)=>{t.constructor.createProperty(i,e)};function O(e){return(t,i)=>i!==void 0?Be(e,t,i):Re(e,t)}var j,st=((j=window.HTMLSlotElement)===null||j===void 0?void 0:j.prototype.assignedElements)!=null?(e,t)=>e.assignedElements(t):(e,t)=>e.assignedNodes(t).filter(i=>i.nodeType===Node.ELEMENT_NODE),z=window,q=z.ShadowRoot&&(z.ShadyCSS===void 0||z.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,K=Symbol(),ce=new WeakMap,de=class{constructor(e,t,i){if(this._$cssResult$=!0,i!==K)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(q&&e===void 0){const i=t!==void 0&&t.length===1;i&&(e=ce.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),i&&ce.set(t,e))}return e}toString(){return this.cssText}},De=e=>new de(typeof e=="string"?e:e+"",void 0,K),P=(e,...t)=>{const i=e.length===1?e[0]:t.reduce((s,r,a)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(r)+e[a+1],e[0]);return new de(i,e,K)},Ve=(e,t)=>{q?e.adoptedStyleSheets=t.map(i=>i instanceof CSSStyleSheet?i:i.styleSheet):t.forEach(i=>{const s=document.createElement("style"),r=z.litNonce;r!==void 0&&s.setAttribute("nonce",r),s.textContent=i.cssText,e.appendChild(s)})},ue=q?e=>e:e=>e instanceof CSSStyleSheet?(t=>{let i="";for(const s of t.cssRules)i+=s.cssText;return De(i)})(e):e,W,L=window,pe=L.trustedTypes,je=pe?pe.emptyScript:"",ve=L.reactiveElementPolyfillSupport,F={toAttribute(e,t){switch(t){case Boolean:e=e?je:null;break;case Object:case Array:e=e==null?e:JSON.stringify(e)}return e},fromAttribute(e,t){let i=e;switch(t){case Boolean:i=e!==null;break;case Number:i=e===null?null:Number(e);break;case Object:case Array:try{i=JSON.parse(e)}catch{i=null}}return i}},fe=(e,t)=>t!==e&&(t==t||e==e),J={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:fe},Z="finalized",g=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this.u()}static addInitializer(e){var t;this.finalize(),((t=this.h)!==null&&t!==void 0?t:this.h=[]).push(e)}static get observedAttributes(){this.finalize();const e=[];return this.elementProperties.forEach((t,i)=>{const s=this._$Ep(i,t);s!==void 0&&(this._$Ev.set(s,i),e.push(s))}),e}static createProperty(e,t=J){if(t.state&&(t.attribute=!1),this.finalize(),this.elementProperties.set(e,t),!t.noAccessor&&!this.prototype.hasOwnProperty(e)){const i=typeof e=="symbol"?Symbol():"__"+e,s=this.getPropertyDescriptor(e,i,t);s!==void 0&&Object.defineProperty(this.prototype,e,s)}}static getPropertyDescriptor(e,t,i){return{get(){return this[t]},set(s){const r=this[e];this[t]=s,this.requestUpdate(e,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)||J}static finalize(){if(this.hasOwnProperty(Z))return!1;this[Z]=!0;const e=Object.getPrototypeOf(this);if(e.finalize(),e.h!==void 0&&(this.h=[...e.h]),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,i=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of i)this.createProperty(s,t[s])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const i=new Set(e.flat(1/0).reverse());for(const s of i)t.unshift(ue(s))}else e!==void 0&&t.push(ue(e));return t}static _$Ep(e,t){const i=t.attribute;return i===!1?void 0:typeof i=="string"?i:typeof e=="string"?e.toLowerCase():void 0}u(){var e;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),(e=this.constructor.h)===null||e===void 0||e.forEach(t=>t(this))}addController(e){var t,i;((t=this._$ES)!==null&&t!==void 0?t:this._$ES=[]).push(e),this.renderRoot!==void 0&&this.isConnected&&((i=e.hostConnected)===null||i===void 0||i.call(e))}removeController(e){var t;(t=this._$ES)===null||t===void 0||t.splice(this._$ES.indexOf(e)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((e,t)=>{this.hasOwnProperty(t)&&(this._$Ei.set(t,this[t]),delete this[t])})}createRenderRoot(){var e;const t=(e=this.shadowRoot)!==null&&e!==void 0?e:this.attachShadow(this.constructor.shadowRootOptions);return Ve(t,this.constructor.elementStyles),t}connectedCallback(){var e;this.renderRoot===void 0&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),(e=this._$ES)===null||e===void 0||e.forEach(t=>{var i;return(i=t.hostConnected)===null||i===void 0?void 0:i.call(t)})}enableUpdating(e){}disconnectedCallback(){var e;(e=this._$ES)===null||e===void 0||e.forEach(t=>{var i;return(i=t.hostDisconnected)===null||i===void 0?void 0:i.call(t)})}attributeChangedCallback(e,t,i){this._$AK(e,i)}_$EO(e,t,i=J){var s;const r=this.constructor._$Ep(e,i);if(r!==void 0&&i.reflect===!0){const a=(((s=i.converter)===null||s===void 0?void 0:s.toAttribute)!==void 0?i.converter:F).toAttribute(t,i.type);this._$El=e,a==null?this.removeAttribute(r):this.setAttribute(r,a),this._$El=null}}_$AK(e,t){var i;const s=this.constructor,r=s._$Ev.get(e);if(r!==void 0&&this._$El!==r){const a=s.getPropertyOptions(r),n=typeof a.converter=="function"?{fromAttribute:a.converter}:((i=a.converter)===null||i===void 0?void 0:i.fromAttribute)!==void 0?a.converter:F;this._$El=r,this[r]=n.fromAttribute(t,a.type),this._$El=null}}requestUpdate(e,t,i){let s=!0;e!==void 0&&(((i=i||this.constructor.getPropertyOptions(e)).hasChanged||fe)(this[e],t)?(this._$AL.has(e)||this._$AL.set(e,t),i.reflect===!0&&this._$El!==e&&(this._$EC===void 0&&(this._$EC=new Map),this._$EC.set(e,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}_$Ej(){return Ie(this,null,function*(){this.isUpdatePending=!0;try{yield this._$E_}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&(yield e),!this.isUpdatePending})}scheduleUpdate(){return this.performUpdate()}performUpdate(){var e;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((s,r)=>this[r]=s),this._$Ei=void 0);let t=!1;const i=this._$AL;try{t=this.shouldUpdate(i),t?(this.willUpdate(i),(e=this._$ES)===null||e===void 0||e.forEach(s=>{var r;return(r=s.hostUpdate)===null||r===void 0?void 0:r.call(s)}),this.update(i)):this._$Ek()}catch(s){throw t=!1,this._$Ek(),s}t&&this._$AE(i)}willUpdate(e){}_$AE(e){var t;(t=this._$ES)===null||t===void 0||t.forEach(i=>{var s;return(s=i.hostUpdated)===null||s===void 0?void 0:s.call(i)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(e){return!0}update(e){this._$EC!==void 0&&(this._$EC.forEach((t,i)=>this._$EO(i,this[i],t)),this._$EC=void 0),this._$Ek()}updated(e){}firstUpdated(e){}};g[Z]=!0,g.elementProperties=new Map,g.elementStyles=[],g.shadowRootOptions={mode:"open"},ve?.({ReactiveElement:g}),((W=L.reactiveElementVersions)!==null&&W!==void 0?W:L.reactiveElementVersions=[]).push("1.6.2");var X,N=window,y=N.trustedTypes,me=y?y.createPolicy("lit-html",{createHTML:e=>e}):void 0,Y="$lit$",v=`lit$${(Math.random()+"").slice(9)}$`,be="?"+v,qe=`<${be}>`,f=document,x=()=>f.createComment(""),T=e=>e===null||typeof e!="object"&&typeof e!="function",ge=Array.isArray,Ke=e=>ge(e)||typeof e?.[Symbol.iterator]=="function",G=`[ 	
\f\r]`,H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ye=/-->/g,_e=/>/g,m=RegExp(`>|${G}(?:([^\\s"'>=/]+)(${G}*=${G}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),$e=/'/g,Ee=/"/g,we=/^(?:script|style|textarea|title)$/i,Ae=e=>(t,...i)=>({_$litType$:e,strings:t,values:i}),Q=Ae(1),rt=Ae(2),_=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),Ce=new WeakMap,b=f.createTreeWalker(f,129,null,!1);function Se(e,t){if(!Array.isArray(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return me!==void 0?me.createHTML(t):t}var We=(e,t)=>{const i=e.length-1,s=[];let r,a=t===2?"<svg>":"",n=H;for(let l=0;l<i;l++){const o=e[l];let d,h,c=-1,p=0;for(;p<o.length&&(n.lastIndex=p,h=n.exec(o),h!==null);)p=n.lastIndex,n===H?h[1]==="!--"?n=ye:h[1]!==void 0?n=_e:h[2]!==void 0?(we.test(h[2])&&(r=RegExp("</"+h[2],"g")),n=m):h[3]!==void 0&&(n=m):n===m?h[0]===">"?(n=r??H,c=-1):h[1]===void 0?c=-2:(c=n.lastIndex-h[2].length,d=h[1],n=h[3]===void 0?m:h[3]==='"'?Ee:$e):n===Ee||n===$e?n=m:n===ye||n===_e?n=H:(n=m,r=void 0);const B=n===m&&e[l+1].startsWith("/>")?" ":"";a+=n===H?o+qe:c>=0?(s.push(d),o.slice(0,c)+Y+o.slice(c)+v+B):o+v+(c===-2?(s.push(void 0),l):B)}return[Se(e,a+(e[i]||"<?>")+(t===2?"</svg>":"")),s]},M=class{constructor({strings:e,_$litType$:t},i){let s;this.parts=[];let r=0,a=0;const n=e.length-1,l=this.parts,[o,d]=We(e,t);if(this.el=M.createElement(o,i),b.currentNode=this.el.content,t===2){const h=this.el.content,c=h.firstChild;c.remove(),h.append(...c.childNodes)}for(;(s=b.nextNode())!==null&&l.length<n;){if(s.nodeType===1){if(s.hasAttributes()){const h=[];for(const c of s.getAttributeNames())if(c.endsWith(Y)||c.startsWith(v)){const p=d[a++];if(h.push(c),p!==void 0){const B=s.getAttribute(p.toLowerCase()+Y).split(v),D=/([.?@])?(.*)/.exec(p);l.push({type:1,index:r,name:D[2],strings:B,ctor:D[1]==="."?Je:D[1]==="?"?Xe:D[1]==="@"?Ye:I})}else l.push({type:6,index:r})}for(const c of h)s.removeAttribute(c)}if(we.test(s.tagName)){const h=s.textContent.split(v),c=h.length-1;if(c>0){s.textContent=y?y.emptyScript:"";for(let p=0;p<c;p++)s.append(h[p],x()),b.nextNode(),l.push({type:2,index:++r});s.append(h[c],x())}}}else if(s.nodeType===8)if(s.data===be)l.push({type:2,index:r});else{let h=-1;for(;(h=s.data.indexOf(v,h+1))!==-1;)l.push({type:7,index:r}),h+=v.length-1}r++}}static createElement(e,t){const i=f.createElement("template");return i.innerHTML=e,i}};function E(e,t,i=e,s){var r,a,n,l;if(t===_)return t;let o=s!==void 0?(r=i._$Co)===null||r===void 0?void 0:r[s]:i._$Cl;const d=T(t)?void 0:t._$litDirective$;return o?.constructor!==d&&((a=o?._$AO)===null||a===void 0||a.call(o,!1),d===void 0?o=void 0:(o=new d(e),o._$AT(e,i,s)),s!==void 0?((n=(l=i)._$Co)!==null&&n!==void 0?n:l._$Co=[])[s]=o:i._$Cl=o),o!==void 0&&(t=E(e,o._$AS(e,t.values),o,s)),t}var Fe=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){var t;const{el:{content:i},parts:s}=this._$AD,r=((t=e?.creationScope)!==null&&t!==void 0?t:f).importNode(i,!0);b.currentNode=r;let a=b.nextNode(),n=0,l=0,o=s[0];for(;o!==void 0;){if(n===o.index){let d;o.type===2?d=new U(a,a.nextSibling,this,e):o.type===1?d=new o.ctor(a,o.name,o.strings,this,e):o.type===6&&(d=new Ge(a,this,e)),this._$AV.push(d),o=s[++l]}n!==o?.index&&(a=b.nextNode(),n++)}return b.currentNode=f,r}v(e){let t=0;for(const i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},U=class{constructor(e,t,i,s){var r;this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=s,this._$Cp=(r=s?.isConnected)===null||r===void 0||r}get _$AU(){var e,t;return(t=(e=this._$AM)===null||e===void 0?void 0:e._$AU)!==null&&t!==void 0?t:this._$Cp}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=E(this,e,t),T(e)?e===u||e==null||e===""?(this._$AH!==u&&this._$AR(),this._$AH=u):e!==this._$AH&&e!==_&&this._(e):e._$litType$!==void 0?this.g(e):e.nodeType!==void 0?this.$(e):Ke(e)?this.T(e):this._(e)}k(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}$(e){this._$AH!==e&&(this._$AR(),this._$AH=this.k(e))}_(e){this._$AH!==u&&T(this._$AH)?this._$AA.nextSibling.data=e:this.$(f.createTextNode(e)),this._$AH=e}g(e){var t;const{values:i,_$litType$:s}=e,r=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=M.createElement(Se(s.h,s.h[0]),this.options)),s);if(((t=this._$AH)===null||t===void 0?void 0:t._$AD)===r)this._$AH.v(i);else{const a=new Fe(r,this),n=a.u(this.options);a.v(i),this.$(n),this._$AH=a}}_$AC(e){let t=Ce.get(e.strings);return t===void 0&&Ce.set(e.strings,t=new M(e)),t}T(e){ge(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let i,s=0;for(const r of e)s===t.length?t.push(i=new U(this.k(x()),this.k(x()),this,this.options)):i=t[s],i._$AI(r),s++;s<t.length&&(this._$AR(i&&i._$AB.nextSibling,s),t.length=s)}_$AR(e=this._$AA.nextSibling,t){var i;for((i=this._$AP)===null||i===void 0||i.call(this,!1,!0,t);e&&e!==this._$AB;){const s=e.nextSibling;e.remove(),e=s}}setConnected(e){var t;this._$AM===void 0&&(this._$Cp=e,(t=this._$AP)===null||t===void 0||t.call(this,e))}},I=class{constructor(e,t,i,s,r){this.type=1,this._$AH=u,this._$AN=void 0,this.element=e,this.name=t,this._$AM=s,this.options=r,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=u}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(e,t=this,i,s){const r=this.strings;let a=!1;if(r===void 0)e=E(this,e,t,0),a=!T(e)||e!==this._$AH&&e!==_,a&&(this._$AH=e);else{const n=e;let l,o;for(e=r[0],l=0;l<r.length-1;l++)o=E(this,n[i+l],t,l),o===_&&(o=this._$AH[l]),a||(a=!T(o)||o!==this._$AH[l]),o===u?e=u:e!==u&&(e+=(o??"")+r[l+1]),this._$AH[l]=o}a&&!s&&this.j(e)}j(e){e===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},Je=class extends I{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===u?void 0:e}},Ze=y?y.emptyScript:"",Xe=class extends I{constructor(){super(...arguments),this.type=4}j(e){e&&e!==u?this.element.setAttribute(this.name,Ze):this.element.removeAttribute(this.name)}},Ye=class extends I{constructor(e,t,i,s,r){super(e,t,i,s,r),this.type=5}_$AI(e,t=this){var i;if((e=(i=E(this,e,t,0))!==null&&i!==void 0?i:u)===_)return;const s=this._$AH,r=e===u&&s!==u||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,a=e!==u&&(s===u||r);r&&this.element.removeEventListener(this.name,this,s),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){var t,i;typeof this._$AH=="function"?this._$AH.call((i=(t=this.options)===null||t===void 0?void 0:t.host)!==null&&i!==void 0?i:this.element,e):this._$AH.handleEvent(e)}},Ge=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){E(this,e)}},ke=N.litHtmlPolyfillSupport;ke?.(M,U),((X=N.litHtmlVersions)!==null&&X!==void 0?X:N.litHtmlVersions=[]).push("2.7.5");var ee=(e,t,i)=>{var s,r;const a=(s=i?.renderBefore)!==null&&s!==void 0?s:t;let n=a._$litPart$;if(n===void 0){const l=(r=i?.renderBefore)!==null&&r!==void 0?r:null;a._$litPart$=n=new U(t.insertBefore(x(),l),l,void 0,i??{})}return n._$AI(e),n},te,ie,w=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var e,t;const i=super.createRenderRoot();return(e=(t=this.renderOptions).renderBefore)!==null&&e!==void 0||(t.renderBefore=i.firstChild),i}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=ee(t,this.renderRoot,this.renderOptions)}connectedCallback(){var e;super.connectedCallback(),(e=this._$Do)===null||e===void 0||e.setConnected(!0)}disconnectedCallback(){var e;super.disconnectedCallback(),(e=this._$Do)===null||e===void 0||e.setConnected(!1)}render(){return _}};w.finalized=!0,w._$litElement$=!0,(te=globalThis.litElementHydrateSupport)===null||te===void 0||te.call(globalThis,{LitElement:w});var Oe=globalThis.litElementPolyfillSupport;Oe?.({LitElement:w}),((ie=globalThis.litElementVersions)!==null&&ie!==void 0?ie:globalThis.litElementVersions=[]).push("3.3.2");var R=class extends w{connectedCallback(){this.maybeCarryFill(),super.connectedCallback()}render(){return Q`<slot></slot>`}maybeCarryFill(){this.isFillCarrier?(this.classList.add("html-fill-container"),this.classList.add("html-fill-item")):(this.classList.remove("html-fill-container"),this.classList.remove("html-fill-item"))}get isFillCarrier(){if(!this.parentElement)return!1;const e=this.parentElement.classList.contains("html-fill-container"),t=Array.from(this.children).some(i=>i.classList.contains("html-fill-item"));return e&&t}};R.isShinyInput=!1,R.styles=P`
    :host {
      display: contents;
    }
  `;function Pe(e){const t=e.querySelector(":scope > [data-bs-toggle='tooltip']");if(t)return t;const i=e.querySelector(":scope > [data-bs-toggle='popover']");if(i)return i;if(e.children.length>1)return e.children[e.children.length-1];if(e.childNodes.length>1){const s=document.createElement("span");return s.append(e.childNodes[e.childNodes.length-1]),e.appendChild(s),s}return e}function xe(e){var t;const{instance:i,trigger:s,content:r,type:a}=e,{tip:n}=i;if(!(n&&n.offsetParent!==null)){i.setContent(r);return}for(const[o,d]of Object.entries(r)){let h=n.querySelector(o);if(!h&&o===".popover-header"){const c=document.createElement("div");c.classList.add("popover-header"),(t=n.querySelector(".popover-body"))==null||t.before(c),h=c}if(!h){console.warn(`Could not find ${o} in ${a} content`);continue}h instanceof HTMLElement?h.replaceChildren(d):h.innerHTML=d}i.update(),s.addEventListener(`hidden.bs.${a}`,()=>i.setContent(r),{once:!0})}function se(e,t){const i=document.createElement("div");return i.style.display=t,e instanceof DocumentFragment?i.append(e):i.innerHTML=e,i}var Te=class{constructor(){this.resizeObserverEntries=[],this.resizeObserver=new ResizeObserver(e=>{const t=new Event("resize");if(window.dispatchEvent(t),!window.Shiny)return;const i=[];for(const s of e)s.target instanceof HTMLElement&&s.target.querySelector(".shiny-bound-output")&&s.target.querySelectorAll(".shiny-bound-output").forEach(r=>{if(i.includes(r))return;const{binding:a,onResize:n}=$(r).data("shinyOutputBinding");if(!a||!a.resize)return;const l=r.shinyResizeObserver;if(l&&l!==this||(l||(r.shinyResizeObserver=this),n(r),i.push(r),!r.classList.contains("shiny-plot-output")))return;const o=r.querySelector('img:not([width="100%"])');o&&o.setAttribute("width","100%")})})}observe(e){this.resizeObserver.observe(e),this.resizeObserverEntries.push(e)}unobserve(e){const t=this.resizeObserverEntries.indexOf(e);t<0||(this.resizeObserver.unobserve(e),this.resizeObserverEntries.splice(t,1))}flush(){this.resizeObserverEntries.forEach(e=>{document.body.contains(e)||this.unobserve(e)})}},Qe=window.bootstrap?window.bootstrap.Tooltip:class{},re=class extends R{constructor(){super(),this.placement="auto",this.bsOptions="{}",this.visible=!1,this.onChangeCallback=e=>{},this._onShown=this._onShown.bind(this),this._onInsert=this._onInsert.bind(this),this._onHidden=this._onHidden.bind(this)}get options(){const e=JSON.parse(this.bsOptions);return V({title:this.content,placement:this.placement,html:!0,sanitize:!1},e)}get content(){return this.children[0]}get triggerElement(){return Pe(this)}get visibleTrigger(){const e=this.triggerElement;return e&&e.offsetParent!==null}connectedCallback(){super.connectedCallback();const e=this.querySelector("template");this.prepend(se(e.content,"none")),e.remove();const t=this.triggerElement;t.setAttribute("data-bs-toggle","tooltip"),t.setAttribute("tabindex","0"),this.bsTooltip=new Qe(t,this.options),t.addEventListener("shown.bs.tooltip",this._onShown),t.addEventListener("hidden.bs.tooltip",this._onHidden),t.addEventListener("inserted.bs.tooltip",this._onInsert),this.visibilityObserver=this._createVisibilityObserver()}disconnectedCallback(){const e=this.triggerElement;e.removeEventListener("shown.bs.tooltip",this._onShown),e.removeEventListener("hidden.bs.tooltip",this._onHidden),e.removeEventListener("inserted.bs.tooltip",this._onInsert),this.visibilityObserver.disconnect(),this.bsTooltip.dispose(),super.disconnectedCallback()}getValue(){return this.visible}_onShown(){this.visible=!0,this.onChangeCallback(!0),this.visibilityObserver.observe(this.triggerElement)}_onHidden(){this.visible=!1,this.onChangeCallback(!0),this._restoreContent(),this.visibilityObserver.unobserve(this.triggerElement),re.shinyResizeObserver.flush()}_onInsert(){var e;const{tip:t}=this.bsTooltip;if(!t)throw new Error("Failed to find the tooltip's DOM element. Please report this bug.");re.shinyResizeObserver.observe(t);const i=(e=t.querySelector(".tooltip-inner"))==null?void 0:e.firstChild;i instanceof HTMLElement&&(i.style.display="contents"),this.bsTooltipEl=t}_restoreContent(){var e;const t=this.bsTooltipEl;if(!t)return;const i=(e=t.querySelector(".tooltip-inner"))==null?void 0:e.firstChild;i instanceof HTMLElement&&(i.style.display="none",this.prepend(i)),this.bsTooltipEl=void 0}receiveMessage(e,t){const i=t.method;if(i==="toggle")this._toggle(t.value);else if(i==="update")this._updateTitle(t.title);else throw new Error(`Unknown method ${i}`)}_toggle(e){(e==="toggle"||e===void 0)&&(e=this.visible?"hide":"show"),e==="hide"&&this.bsTooltip.hide(),e==="show"&&this._show()}_show(){!this.visible&&this.visibleTrigger&&this.bsTooltip.show()}_updateTitle(e){e&&(Shiny.renderDependencies(e.deps),xe({instance:this.bsTooltip,trigger:this.triggerElement,content:{".tooltip-inner":e.html},type:"tooltip"}))}_createVisibilityObserver(){const e=t=>{this.visible&&t.forEach(i=>{i.isIntersecting||this.bsTooltip.hide()})};return new IntersectionObserver(e)}},A=re;A.tagName="bslib-tooltip",A.shinyResizeObserver=new Te,A.isShinyInput=!0,k([O({type:String})],A.prototype,"placement",2),k([O({type:String})],A.prototype,"bsOptions",2);var et=window.bootstrap?window.bootstrap.Popover:class{},ne=class extends R{constructor(){super(),this.placement="auto",this.bsOptions="{}",this.visible=!1,this.onChangeCallback=e=>{},this._onShown=this._onShown.bind(this),this._onInsert=this._onInsert.bind(this),this._onHidden=this._onHidden.bind(this),this._handleTabKey=this._handleTabKey.bind(this),this._handleEscapeKey=this._handleEscapeKey.bind(this),this._closeButton=this._closeButton.bind(this)}get options(){const e=JSON.parse(this.bsOptions);return V({content:this.content,title:oe(this.header)?this.header:"",placement:this.placement,html:!0,sanitize:!1,trigger:this.isHyperLink?"focus hover":"click"},e)}get content(){return this.contentContainer.children[0]}get header(){return this.contentContainer.children[1]}get contentContainer(){return this.children[0]}get triggerElement(){return Pe(this)}get visibleTrigger(){const e=this.triggerElement;return e&&e.offsetParent!==null}get isButtonLike(){return this.options.trigger==="click"&&this.triggerElement.tagName!=="BUTTON"}get focusablePopover(){return!this.options.trigger.includes("focus")}get isHyperLink(){const e=this.triggerElement;return e.tagName==="A"&&e.hasAttribute("href")&&e.getAttribute("href")!=="#"&&e.getAttribute("href")!==""&&e.getAttribute("href")!=="javascript:void(0)"}connectedCallback(){super.connectedCallback();const e=this.querySelector("template");this.prepend(se(e.content,"none")),e.remove(),this.content&&ee(this._closeButton(this.header),this.content);const t=this.triggerElement;t.setAttribute("data-bs-toggle","popover"),this.isButtonLike&&(t.setAttribute("role","button"),t.setAttribute("tabindex","0"),t.setAttribute("aria-pressed","false"),this.triggerElement.tagName!=="A"&&(t.onkeydown=i=>{(i.key==="Enter"||i.key===" ")&&this._toggle()}),t.style.cursor="pointer"),this.bsPopover=new et(t,this.options),t.addEventListener("shown.bs.popover",this._onShown),t.addEventListener("hidden.bs.popover",this._onHidden),t.addEventListener("inserted.bs.popover",this._onInsert),this.visibilityObserver=this._createVisibilityObserver()}disconnectedCallback(){const e=this.triggerElement;e.removeEventListener("shown.bs.popover",this._onShown),e.removeEventListener("hidden.bs.popover",this._onHidden),e.removeEventListener("inserted.bs.popover",this._onInsert),this.visibilityObserver.disconnect(),this.bsPopover.dispose(),super.disconnectedCallback()}getValue(){return this.visible}_onShown(){this.visible=!0,this.onChangeCallback(!0),this.visibilityObserver.observe(this.triggerElement),this.focusablePopover&&(document.addEventListener("keydown",this._handleTabKey),document.addEventListener("keydown",this._handleEscapeKey)),this.isButtonLike&&this.triggerElement.setAttribute("aria-pressed","true")}_onHidden(){this.visible=!1,this.onChangeCallback(!0),this._restoreContent(),this.visibilityObserver.unobserve(this.triggerElement),ne.shinyResizeObserver.flush(),this.focusablePopover&&(document.removeEventListener("keydown",this._handleTabKey),document.removeEventListener("keydown",this._handleEscapeKey)),this.isButtonLike&&this.triggerElement.setAttribute("aria-pressed","false")}_onInsert(){const{tip:e}=this.bsPopover;if(!e)throw new Error("Failed to find the popover's DOM element. Please report this bug.");ne.shinyResizeObserver.observe(e),this.focusablePopover&&e.setAttribute("tabindex","0"),this.bsPopoverEl=e}_handleTabKey(e){if(e.key!=="Tab")return;const{tip:t}=this.bsPopover;if(!t)return;const i=()=>{e.preventDefault(),e.stopImmediatePropagation()},s=document.activeElement;s===this.triggerElement&&!e.shiftKey&&(i(),t.focus()),s===t&&e.shiftKey&&(i(),this.triggerElement.focus())}_handleEscapeKey(e){if(e.key!=="Escape")return;const{tip:t}=this.bsPopover;if(!t)return;const i=document.activeElement;(i===this.triggerElement||t.contains(i))&&(e.preventDefault(),e.stopImmediatePropagation(),this._hide(),this.triggerElement.focus())}_restoreContent(){const e=this.bsPopoverEl;if(!e)return;const t=e.querySelector(".popover-body");t&&this.contentContainer.append(t?.firstChild);const i=e.querySelector(".popover-header");i&&this.contentContainer.append(i?.firstChild),this.bsPopoverEl=void 0}receiveMessage(e,t){const i=t.method;if(i==="toggle")this._toggle(t.value);else if(i==="update")this._updatePopover(t);else throw new Error(`Unknown method ${i}`)}_toggle(e){(e==="toggle"||e===void 0)&&(e=this.visible?"hide":"show"),e==="hide"&&this._hide(),e==="show"&&this._show()}_hide(){this.bsPopover.hide()}_show(){!this.visible&&this.visibleTrigger&&this.bsPopover.show()}_updatePopover(e){const{content:t,header:i}=e,s=[];t&&s.push(...t.deps),i&&s.push(...i.deps),Shiny.renderDependencies(s);const r=(l,o,d)=>{var h;return l?se(l.html,"contents"):o||((h=this.bsPopover.tip)==null?void 0:h.querySelector(d))},a=r(i,this.header,".popover-header"),n=r(t,this.content,".popover-body");ee(this._closeButton(a),n),xe({instance:this.bsPopover,trigger:this.triggerElement,content:{".popover-header":oe(a)?a:"",".popover-body":n},type:"popover"})}_closeButton(e){if(!this.focusablePopover)return u;const t=()=>{this._hide(),this.focusablePopover&&this.triggerElement.focus()},i=oe(e)?"0.6rem":"0.25rem";return Q`<button
      type="button"
      aria-label="Close"
      class="btn-close"
      @click=${t}
      style="position:absolute; top:${i}; right:0.25rem; width:0.55rem; height:0.55rem; background-size:0.55rem;"
    ></button>`}_createVisibilityObserver(){const e=t=>{this.visible&&t.forEach(i=>{i.isIntersecting||this._hide()})};return new IntersectionObserver(e)}},C=ne;C.tagName="bslib-popover",C.shinyResizeObserver=new Te,C.isShinyInput=!0,k([O({type:String})],C.prototype,"placement",2),k([O({type:String})],C.prototype,"bsOptions",2);function oe(e){return!!e&&e.childNodes.length>0}var S=class extends w{constructor(){super(...arguments),this.attribute="data-shinytheme",this.onChangeCallback=e=>{}}connectedCallback(){super.connectedCallback(),this.attribute=this.getAttribute("attribute")||this.attribute,typeof this.mode>"u"&&(this.mode=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"),this.reflectPreference(),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",({matches:e})=>{this.mode=e?"dark":"light",this.reflectPreference()}),this._observeDocumentThemeAttribute()}disconnectedCallback(){this.observer.disconnect(),super.disconnectedCallback()}_observeDocumentThemeAttribute(){this.observer=new MutationObserver(t=>{t.forEach(i=>{if(i.target!==document.documentElement||i.attributeName!==this.attribute)return;const s=document.documentElement.getAttribute(this.attribute);!s||s===this.mode||(this.mode=s)})});const e={attributes:!0,childList:!1,subtree:!1};this.observer.observe(document.documentElement,e)}getValue(){return this.mode}render(){const e=this.mode==="light"?"dark":"light",t=`Switch from ${this.mode} to ${e} mode`;return Q`
      <button
        title="${t}"
        aria-label="${t}"
        aria-live="polite"
        data-theme="${this.mode}"
        @click="${this.onClick}"
      >
        <svg class="sun-and-moon" aria-hidden="true" viewBox="0 0 24 24">
          <mask class="moon" id="moon-mask">
            <rect x="0" y="0" width="100%" height="100%" fill="white" />
            <circle cx="25" cy="10" r="6" fill="black" />
          </mask>
          <circle
            class="sun"
            cx="12"
            cy="12"
            r="6"
            mask="url(#moon-mask)"
            fill="currentColor"
          />
          <g class="sun-beams" stroke="currentColor">
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </g>
        </svg>
      </button>
    `}onClick(e){e.stopPropagation(),this.mode=this.mode==="light"?"dark":"light"}updated(e){e.has("mode")&&(this.reflectPreference(),this.onChangeCallback(!0))}reflectPreference(){document.documentElement.setAttribute(this.attribute,this.mode),window.dispatchEvent(new Event("resize"))}};S.isShinyInput=!0,S.tagName="bslib-input-dark-mode",S.shinyCustomMessageHandlers={"bslib.toggle-dark-mode":({method:e,value:t})=>{e==="toggle"&&((typeof t>"u"||t===null)&&(t=(document.documentElement.dataset.bsTheme||"light")==="light"?"dark":"light"),document.documentElement.dataset.bsTheme=t)}},S.styles=[P`
      :host {
        /* open-props.style via shinycomponent */
        --text-1: var(--text-1-light, var(--gray-8, #343a40));
        --text-2: var(--text-2-light, var(--gray-7, #495057));
        --size-xxs: var(--size-1, 0.25rem);
        --ease-in-out-1: cubic-bezier(0.1, 0, 0.9, 1);
        --ease-in-out-2: cubic-bezier(0.3, 0, 0.7, 1);
        --ease-out-1: cubic-bezier(0, 0, 0.75, 1);
        --ease-out-3: cubic-bezier(0, 0, 0.3, 1);
        --ease-out-4: cubic-bezier(0, 0, 0.1, 1);

        /* shinycomponent */
        --speed-fast: 0.15s;
        --speed-normal: 0.3s;

        /* Size of the icon, uses em units so it scales to font-size */
        --size: 1.3em;

        /* Because we are (most likely) bigger than one em we will need to move
        the button up or down to keep it looking right inline */
        --vertical-correction: calc((var(--size) - 1em) / 2);
      }
    `,P`
      .sun-and-moon > :is(.moon, .sun, .sun-beams) {
        transform-origin: center center;
      }

      .sun-and-moon > .sun {
        fill: none;
        stroke: var(--text-1);
        stroke-width: var(--stroke-w);
      }

      button:is(:hover, :focus-visible)
        > :is(.sun-and-moon > :is(.moon, .sun)) {
        fill: var(--text-2);
      }

      .sun-and-moon > .sun-beams {
        stroke: var(--text-1);
        stroke-width: var(--stroke-w);
      }

      button:is(:hover, :focus-visible) :is(.sun-and-moon > .sun-beams) {
        background-color: var(--text-2);
      }

      [data-theme="dark"] .sun-and-moon > .sun {
        fill: var(--text-1);
        stroke: none;
        stroke-width: 0;
        transform: scale(1.6);
      }

      [data-theme="dark"] .sun-and-moon > .sun-beams {
        opacity: 0;
      }

      [data-theme="dark"] .sun-and-moon > .moon > circle {
        transform: translateX(-10px);
      }

      @supports (cx: 1) {
        [data-theme="dark"] .sun-and-moon > .moon > circle {
          transform: translateX(0);
          cx: 15;
        }
      }
    `,P`
      .sun-and-moon > .sun {
        transition: transform var(--speed-fast) var(--ease-in-out-2)
            var(--speed-fast),
          fill var(--speed-fast) var(--ease-in-out-2) var(--speed-fast),
          stroke-width var(--speed-normal) var(--ease-in-out-2);
      }

      .sun-and-moon > .sun-beams {
        transition: transform var(--speed-fast) var(--ease-out-3),
          opacity var(--speed-fast) var(--ease-out-4);
        transition-delay: var(--speed-normal);
      }

      .sun-and-moon .moon > circle {
        transition: transform var(--speed-fast) var(--ease-in-out-2),
          fill var(--speed-fast) var(--ease-in-out-2);
        transition-delay: 0s;
      }

      @supports (cx: 1) {
        .sun-and-moon .moon > circle {
          transition: cx var(--speed-normal) var(--ease-in-out-2);
        }

        [data-theme="dark"] .sun-and-moon .moon > circle {
          transition: cx var(--speed-fast) var(--ease-in-out-2);
          transition-delay: var(--speed-fast);
        }
      }

      [data-theme="dark"] .sun-and-moon > .sun {
        transition-delay: 0s;
        transition-duration: var(--speed-normal);
        transition-timing-function: var(--ease-in-out-2);
      }

      [data-theme="dark"] .sun-and-moon > .sun-beams {
        transform: scale(0.3);
        transition: transform var(--speed-normal) var(--ease-in-out-2),
          opacity var(--speed-fast) var(--ease-out-1);
        transition-delay: 0s;
      }
    `,P`
      :host {
        display: inline-block;

        /* We control the stroke size manually here. We don't want it getting so
        small its not visible but also not so big it looks cartoonish */
        --stroke-w: clamp(1px, 0.1em, 6px);
      }

      button {
        /* This is needed to let the svg use the em sizes */
        font-size: inherit;

        /* Make sure the button is fully centered */
        display: grid;
        place-content: center;

        /* A little bit of padding to make it easier to press */
        padding: var(--size-xxs);
        background: none;
        border: none;
        aspect-ratio: 1;
        border-radius: 50%;
        cursor: pointer;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
        outline-offset: var(--size-xxs);

        /* Move down to adjust for being larger than 1em */
        transform: translateY(var(--vertical-correction));
        margin-block-end: var(--vertical-correction);
      }

      /*
      button:is(:hover, :focus-visible) {
        background: var(--surface-4);
      }
      */

      button > svg {
        height: var(--size);
        width: var(--size);
        stroke-linecap: round;
        overflow: visible;
      }

      svg line,
      svg circle {
        vector-effect: non-scaling-stroke;
      }
    `],k([O({type:String,reflect:!0})],S.prototype,"mode",2);function tt(e,{type:t=null}={}){if(!window.Shiny)return;class i extends Shiny.InputBinding{constructor(){super()}find(r){return $(r).find(e)}getValue(r){return"getValue"in r?r.getValue():r.value}getType(r){return t}subscribe(r,a){r.onChangeCallback=a}unsubscribe(r){r.onChangeCallback=a=>{}}receiveMessage(r,a){r.receiveMessage(r,a)}}Shiny.inputBindings.register(new i,`${e}-Binding`)}function it(e){if(window.Shiny)for(const[t,i]of Object.entries(e))Shiny.addCustomMessageHandler(t,i)}[A,C,S].forEach(e=>{customElements.define(e.tagName,e),window.Shiny&&(e.isShinyInput&&tt(e.tagName),"shinyCustomMessageHandlers"in e&&it(e.shinyCustomMessageHandlers))})})();/*! Bundled license information:

@lit/reactive-element/decorators/custom-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/property.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/state.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/base.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/event-options.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-all.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-async.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/lit-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
