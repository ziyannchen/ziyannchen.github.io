(self["webpackChunkfos_user_study_page"]=self["webpackChunkfos_user_study_page"]||[]).push([[664],{83855:function(e,t,r){var a=Object.create,n=Object.defineProperty,i=Object.getOwnPropertyDescriptor,l=Object.getOwnPropertyNames,s=Object.getPrototypeOf,o=Object.prototype.hasOwnProperty,p=(e,t,r)=>t in e?n(e,t,{enumerable:!0,configurable:!0,writable:!0,value:r}):e[t]=r,u=(e,t)=>{for(var r in t)n(e,r,{get:t[r],enumerable:!0})},c=(e,t,r,a)=>{if(t&&"object"===typeof t||"function"===typeof t)for(let s of l(t))o.call(e,s)||s===r||n(e,s,{get:()=>t[s],enumerable:!(a=i(t,s))||a.enumerable});return e},d=(e,t,r)=>(r=null!=e?a(s(e)):{},c(!t&&e&&e.__esModule?r:n(r,"default",{value:e,enumerable:!0}),e)),h=e=>c(n({},"__esModule",{value:!0}),e),m=(e,t,r)=>(p(e,"symbol"!==typeof t?t+"":t,r),r),g={};u(g,{default:()=>_}),e.exports=h(g);var b=d(r(67294));const f="64px",y={};class _ extends b.Component{constructor(){super(...arguments),m(this,"mounted",!1),m(this,"state",{image:null}),m(this,"handleKeyPress",(e=>{"Enter"!==e.key&&" "!==e.key||this.props.onClick()}))}componentDidMount(){this.mounted=!0,this.fetchImage(this.props)}componentDidUpdate(e){const{url:t,light:r}=this.props;e.url===t&&e.light===r||this.fetchImage(this.props)}componentWillUnmount(){this.mounted=!1}fetchImage({url:e,light:t,oEmbedUrl:r}){if(!b.default.isValidElement(t))if("string"!==typeof t){if(!y[e])return this.setState({image:null}),window.fetch(r.replace("{url}",e)).then((e=>e.json())).then((t=>{if(t.thumbnail_url&&this.mounted){const r=t.thumbnail_url.replace("height=100","height=480").replace("-d_295x166","-d_640");this.setState({image:r}),y[e]=r}}));this.setState({image:y[e]})}else this.setState({image:t})}render(){const{light:e,onClick:t,playIcon:r,previewTabIndex:a,previewAriaLabel:n}=this.props,{image:i}=this.state,l=b.default.isValidElement(e),s={display:"flex",alignItems:"center",justifyContent:"center"},o={preview:{width:"100%",height:"100%",backgroundImage:i&&!l?`url(${i})`:void 0,backgroundSize:"cover",backgroundPosition:"center",cursor:"pointer",...s},shadow:{background:"radial-gradient(rgb(0, 0, 0, 0.3), rgba(0, 0, 0, 0) 60%)",borderRadius:f,width:f,height:f,position:l?"absolute":void 0,...s},playIcon:{borderStyle:"solid",borderWidth:"16px 0 16px 26px",borderColor:"transparent transparent transparent white",marginLeft:"7px"}},p=b.default.createElement("div",{style:o.shadow,className:"react-player__shadow"},b.default.createElement("div",{style:o.playIcon,className:"react-player__play-icon"}));return b.default.createElement("div",{style:o.preview,className:"react-player__preview",onClick:t,tabIndex:a,onKeyPress:this.handleKeyPress,...n?{"aria-label":n}:{}},l?e:null,r||p)}}}}]);