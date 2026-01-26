/* [create-plugin] version: 6.7.8 */
/* [create-plugin] plugin: contextcore-workflow-panel@1.0.0 */
define(["@grafana/ui","@emotion/css","module","@grafana/runtime","@grafana/data","react"],(e,t,a,n,r,s)=>(()=>{"use strict";var o={7(t){t.exports=e},89(e){e.exports=t},308(e){e.exports=a},531(e){e.exports=n},781(e){e.exports=r},959(e){e.exports=s}},l={};function c(e){var t=l[e];if(void 0!==t)return t.exports;var a=l[e]={exports:{}};return o[e](a,a.exports,c),a.exports}c.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return c.d(t,{a:t}),t},c.d=(e,t)=>{for(var a in t)c.o(t,a)&&!c.o(e,a)&&Object.defineProperty(e,a,{enumerable:!0,get:t[a]})},c.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),c.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},c.p="public/plugins/contextcore-workflow-panel/";var i={};c.r(i),c.d(i,{plugin:()=>w});var u=c(308),d=c.n(u);c.p=d()&&d().uri?d().uri.slice(0,d().uri.lastIndexOf("/")+1):"public/plugins/contextcore-workflow-panel/";var p=c(781),m=c(959),f=c.n(m),x=c(531),y=c(7),g=c(89);function v(e,t,a,n,r,s,o){try{var l=e[s](o),c=l.value}catch(e){return void a(e)}l.done?t(c):Promise.resolve(c).then(n,r)}function h(e){return function(){var t=this,a=arguments;return new Promise(function(n,r){var s=e.apply(t,a);function o(e){v(s,n,r,o,l,"next",e)}function l(e){v(s,n,r,o,l,"throw",e)}o(void 0)})}}const E=()=>({container:g.css`
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    height: 100%;
    overflow: auto;
  `,header:g.css`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-weak);
  `,projectInfo:g.css`
    display: flex;
    gap: 8px;
    align-items: center;
  `,statusBadge:g.css`
    display: flex;
    align-items: center;
  `,label:g.css`
    font-size: 12px;
    color: var(--text-secondary);
  `,value:g.css`
    font-weight: 500;
    color: var(--text-primary);
  `,buttonRow:g.css`
    display: flex;
    gap: 8px;
  `,loadingSection:g.css`
    display: flex;
    justify-content: center;
    padding: 20px;
  `,stepsSection:g.css`
    background: var(--background-secondary);
    border-radius: 4px;
    padding: 12px;
  `,sectionTitle:g.css`
    font-weight: 500;
    font-size: 13px;
    margin-bottom: 8px;
    color: var(--text-primary);
  `,stepsList:g.css`
    display: flex;
    flex-direction: column;
    gap: 4px;
  `,step:g.css`
    display: flex;
    gap: 8px;
    align-items: center;
    font-size: 12px;
  `,stepStatus:g.css`
    width: 16px;
    text-align: center;
  `,stepName:g.css`
    color: var(--text-primary);
  `,stepReason:g.css`
    color: var(--text-secondary);
    font-style: italic;
  `,lastRunSection:g.css`
    background: var(--background-secondary);
    border-radius: 4px;
    padding: 12px;
  `,lastRunInfo:g.css`
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;

    > div {
      display: flex;
      gap: 8px;
    }
  `}),w=new p.PanelPlugin(({options:e,width:t,height:a})=>{const[n,r]=(0,m.useState)("idle"),[s,o]=(0,m.useState)(null),[l,c]=(0,m.useState)(null),[i,u]=(0,m.useState)(null),[d,p]=(0,m.useState)(!1),[g,v]=(0,m.useState)(null),[w,b]=(0,m.useState)(!1),N=(0,y.useStyles2)(E),S=(0,m.useRef)(null),k=(0,x.getTemplateSrv)().replace(e.projectId);(0,m.useEffect)(()=>("running"===n&&s&&e.refreshInterval>0&&(S.current=setInterval(()=>h(function*(){try{const t=yield fetch(`${e.apiUrl}/workflow/status/${s}`);if(t.ok){const e=yield t.json();c(e),"completed"===e.status?r("completed"):"failed"===e.status&&(r("failed"),v(e.error||"Workflow failed"))}}catch(e){}})(),1e3*e.refreshInterval)),()=>{S.current&&(clearInterval(S.current),S.current=null)}),[n,s,e.apiUrl,e.refreshInterval]);const R=(0,m.useCallback)(()=>h(function*(){p(!0),v(null),u(null);try{const t=yield fetch(`${e.apiUrl}/workflow/dry-run`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({project_id:k})});if(!t.ok)throw new Error(`HTTP ${t.status}: ${t.statusText}`);const a=yield t.json();"success"===a.status?(u(a.steps),o(a.run_id)):v(a.error||"Dry run failed")}catch(e){v(e instanceof Error?e.message:"Failed to connect to Rabbit API")}finally{p(!1)}})(),[e.apiUrl,k]),I=(0,m.useCallback)(()=>h(function*(){e.confirmExecution?b(!0):yield P()})(),[e.confirmExecution]),P=(0,m.useCallback)(()=>h(function*(){p(!0),v(null),r("running"),u(null);try{const t=yield fetch(`${e.apiUrl}/workflow/execute`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({project_id:k})});if(!t.ok)throw new Error(`HTTP ${t.status}: ${t.statusText}`);const a=yield t.json();"started"===a.status?o(a.run_id):(v(a.error||"Failed to start workflow"),r("failed"))}catch(e){v(e instanceof Error?e.message:"Failed to connect to Rabbit API"),r("failed")}finally{p(!1)}})(),[e.apiUrl,k]),j=(0,m.useCallback)(()=>h(function*(){b(!1),yield P()})(),[P]),T=e=>new Date(e).toLocaleString();return f().createElement("div",{className:N.container,style:{width:t,height:a}},f().createElement("div",{className:N.header},f().createElement("div",{className:N.projectInfo},f().createElement("span",{className:N.label},"Project:"),f().createElement("span",{className:N.value},k)),f().createElement("div",{className:N.statusBadge},(()=>{switch(n){case"running":return f().createElement(y.Badge,{text:"Running",color:"blue",icon:"sync"});case"completed":return f().createElement(y.Badge,{text:"Completed",color:"green",icon:"check"});case"failed":return f().createElement(y.Badge,{text:"Failed",color:"red",icon:"exclamation-triangle"});default:return f().createElement(y.Badge,{text:"Idle",color:"purple"})}})())),f().createElement("div",{className:N.buttonRow},e.showDryRun&&f().createElement(y.Button,{onClick:R,disabled:d||"running"===n,variant:"secondary",icon:"sync"},"Dry Run"),e.showExecute&&f().createElement(y.Button,{onClick:I,disabled:d||"running"===n,variant:"primary",icon:"play"},"Execute")),d&&f().createElement("div",{className:N.loadingSection},f().createElement(y.LoadingPlaceholder,{text:"Processing..."})),g&&f().createElement(y.Alert,{severity:"error",title:"Error"},g),i&&f().createElement("div",{className:N.stepsSection},f().createElement("div",{className:N.sectionTitle},"Dry Run Preview"),f().createElement("div",{className:N.stepsList},i.map((e,t)=>f().createElement("div",{key:t,className:N.step},f().createElement("span",{className:N.stepStatus},"would_execute"===e.status?"✓":"would_skip"===e.status?"○":"✗"),f().createElement("span",{className:N.stepName},e.name),e.reason&&f().createElement("span",{className:N.stepReason},"(",e.reason,")"))))),l&&f().createElement("div",{className:N.lastRunSection},f().createElement("div",{className:N.sectionTitle},"Last Run"),f().createElement("div",{className:N.lastRunInfo},f().createElement("div",null,f().createElement("span",{className:N.label},"Run ID:"),f().createElement("span",{className:N.value},l.run_id)),f().createElement("div",null,f().createElement("span",{className:N.label},"Started:"),f().createElement("span",{className:N.value},T(l.started_at))),l.completed_at&&f().createElement("div",null,f().createElement("span",{className:N.label},"Completed:"),f().createElement("span",{className:N.value},T(l.completed_at))),void 0!==l.duration_seconds&&f().createElement("div",null,f().createElement("span",{className:N.label},"Duration:"),f().createElement("span",{className:N.value},(e=>{if(e<60)return`${e}s`;return`${Math.floor(e/60)}m ${e%60}s`})(l.duration_seconds))),f().createElement("div",null,f().createElement("span",{className:N.label},"Progress:"),f().createElement("span",{className:N.value},l.steps_completed,"/",l.steps_total," steps")))),f().createElement(y.ConfirmModal,{isOpen:w,title:"Execute Workflow",body:`Are you sure you want to execute the workflow for project "${k}"?`,confirmText:"Execute",onConfirm:j,onDismiss:()=>b(!1)}))}).setPanelOptions(e=>{e.addTextInput({path:"apiUrl",name:"Rabbit API URL",description:"Base URL of the Rabbit API server",defaultValue:"http://localhost:8080",category:["Connection"]}).addTextInput({path:"projectId",name:"Project ID",description:"Project ID or template variable (e.g., $project)",defaultValue:"$project",category:["Connection"]}).addBooleanSwitch({path:"showDryRun",name:"Show Dry Run Button",description:"Display the Dry Run button for previewing workflow execution",defaultValue:!0,category:["Buttons"]}).addBooleanSwitch({path:"showExecute",name:"Show Execute Button",description:"Display the Execute button for running workflows",defaultValue:!0,category:["Buttons"]}).addBooleanSwitch({path:"confirmExecution",name:"Confirm Execution",description:"Require confirmation before executing workflows",defaultValue:!0,category:["Buttons"]}).addNumberInput({path:"refreshInterval",name:"Auto-Refresh Interval",description:"Auto-refresh status interval in seconds (0 to disable)",defaultValue:10,category:["Display"]})});return i})());
//# sourceMappingURL=module.js.map