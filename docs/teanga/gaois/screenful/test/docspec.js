var blankXml="<article id='' language=''><title></title><body><paragraph/></body></article>";

var docSpec={
	onchange: function(jsSurrogate){
		//console.log(jsSurrogate.parent());
	},
	validate: function(jsElement){
		if(typeof(jsElement)=="string") jsElement=Xonomy.xml2js(jsElement);
		var valid=true;
		var elementSpec=this.elements[jsElement.name];
		if(elementSpec.validate) {
			elementSpec.validate(jsElement); //validate the element
		}
		for(var iAttribute=0; iAttribute<jsElement.attributes.length; iAttribute++) {
			var jsAttribute=jsElement.attributes[iAttribute];
			var attributeSpec=elementSpec.attributes[jsAttribute.name];
			if(attributeSpec.validate) {
				if(!attributeSpec.validate(jsAttribute)) valid=false; //validate the attribute
			}
		}
		for(var iChild=0; iChild<jsElement.children.length; iChild++) {
			if(jsElement.children[iChild].type=="element") {
				var jsChild=jsElement.children[iChild];
				if(!this.validate(jsChild)) valid=false; //recurse to the child element
			}
		}
		return valid;
	},
	elements: {

		//top-level structure:
		"article": {
			collapsible: false,
			validate: function(jsElement) {
				if(!jsElement.hasAttribute("id")) {
					Xonomy.warnings.push({htmlID: jsElement.htmlID, text: "This element is missing an @id attribute."});
					return false;
				}
				return true;
			},
			attributes: {
				"id": {
					asker: Xonomy.askString,
					askerParameter: {},
					menu: [],
					validate: function(jsAttribute) {
						if($.trim(jsAttribute.value)=="") {
							Xonomy.warnings.push({htmlID: jsAttribute.htmlID, text: "en: The @id attribute should not be empty. | ga: Ní cheadaítear an aitreabúid @id a bheith folamh."});
							return false;
						}
						return true;
					},
				},
				"language": {
					asker: Xonomy.askPicklist,
					askerParameter: [
						{value: "en", caption: "en: English | de: Englisch    | ga: Béarla"},
						{value: "ga", caption: "en: Irish   | de: Irisch      | ga: Gaeilge"},
						{value: "de", caption: "en: German  | de: Deutsch     | ga: Gearmáinis"},
						{value: "cs", caption: "en: Czech   | de: Tschechisch | ga: Seicis"},
					],
					caption: function(jsMe){
						if(jsMe.value=="en") return "en: English | de: Englisch    | ga: Béarla";
						if(jsMe.value=="ga") return "en: Irish   | de: Irisch      | ga: Gaeilge";
						if(jsMe.value=="de") return "en: German  | de: Deutsch     | ga: Gearmáinis";
						if(jsMe.value=="cs") return "en: Czech   | de: Tschechisch | ga: Seicis";
					},
					menu: [],
					validate: function(jsAttribute) {
						var has=false;
						for(var i=0; i<this.askerParameter.length; i++) {
							if(this.askerParameter[i].value==jsAttribute.value) has=true;
						}
						if(!has) {
							Xonomy.warnings.push({htmlID: jsAttribute.htmlID, text: "@\""+jsAttribute.value+"\" is not a valid value for the @language attribute."});
							return false;
						}
						return true;
					},
				}
			},
			menu: [],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsed: function(jsElement){return false},
			oneliner: false,
			hasText: false,
			inlineMenu: []
		},
		"title": {
			attributes: {},
			menu: [],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsible: false,
			oneliner: true,
			hasText: true,
			inlineMenu: [],
			asker: Xonomy.askOpenPicklist,
			askerParameter: ["Introduction", "History", "Current Status", "Conclusion"],
			caption: function(jsMe){
				var txt=jsMe.getText();
				if(txt=="Introduction") return "Úvod";
				if(txt=="History") return "Historie";
				if(txt=="Current Status") return "Současný stav";
				if(txt=="Conclusion") return "Závěr";
				//return txt;
			},
		},
		"body": {
			backgroundColour: "#ffd6d6",
			attributes: {},
			menu: [
				{caption: "en: New <paragraph> | ga: <paragraph> nua", action: Xonomy.newElementChild, actionParameter: "<paragraph/>", hideIf: function(jsElement){return false}}
			],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsed: function(jsElement){return false},
			oneliner: false,
			hasText: false,
			inlineMenu: [],
		},

		//block-level textual elements:
		"paragraph": {
			//isReadOnly: true,
			attributes: {},
			menu: [
				{caption: "New <paragraph> before this", action: Xonomy.newElementBefore, actionParameter: "<paragraph/>", hideIf: function(jsElement){return false}},
				{caption: "New <paragraph> after this", action: Xonomy.newElementAfter, actionParameter: "<paragraph/>", hideIf: function(jsElement){return false}},
				{caption: "Delete", action: Xonomy.deleteElement, actionParameter: null, hideIf: function(jsElement){return false}}
			],
			canDropTo: ["body"],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsed: function(jsElement){return false},
			oneliner: false,
			hasText: true,
			inlineMenu: [
				{caption: "<i> (italic)", action: Xonomy.wrap, actionParameter: {template: "<i>$</i>", placeholder: "$"}, hideIf: function(jsElement){return false}},
				{caption: "<b> (bold)", action: Xonomy.wrap, actionParameter: {template: "<b>$</b>", placeholder: "$"}, hideIf: function(jsElement){return false}},
				{caption: "<u> (underline)", action: Xonomy.wrap, actionParameter: {template: "<u>$</u>", placeholder: "$"}, hideIf: function(jsElement){return false}},
				{caption: "<a> (external link)", action: Xonomy.wrap, actionParameter: {template: "<a href=''>$</a>", placeholder: "$"}, hideIf: function(jsElement){return false}},
			]
		},


		//inline textual elements:
		"i": {
			//backgroundColour: "#d6ffd6",
			attributes: {},
			menu: [
				{caption: "Unwrap", action: Xonomy.unwrap, actionParameter: null, hideIf: function(jsElement){return false}}
			],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsible: false,
			oneliner: true,
			hasText: true,
			inlineMenu: [
				{caption: "<b> (bold)", action: Xonomy.wrap, actionParameter: {template: "<b>$</b>", placeholder: "$"}, hideIf: function(jsElement){return false}},
				{caption: "<u> (underline)", action: Xonomy.wrap, actionParameter: {template: "<u>$</u>", placeholder: "$"}, hideIf: function(jsElement){return false}}
			]
		},
		"b": {
			//backgroundColour: "#d6ffd6",
			attributes: {},
			menu: [
				{caption: "Unwrap", action: Xonomy.unwrap, actionParameter: null, hideIf: function(jsElement){return false}}
			],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsible: false,
			oneliner: true,
			hasText: true,
			inlineMenu: [
				{caption: "<i> (italic)", action: Xonomy.wrap, actionParameter: {template: "<i>$</i>", placeholder: "$"}, hideIf: function(jsElement){return false}},
				{caption: "<u> (underline)", action: Xonomy.wrap, actionParameter: {template: "<u>$</u>", placeholder: "$"}, hideIf: function(jsElement){return false}}
			]
		},
		"u": {
			//backgroundColour: "#d6ffd6",
			attributes: {},
			menu: [
				{caption: "Unwrap", action: Xonomy.unwrap, actionParameter: null, hideIf: function(jsElement){return false}}
			],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			collapsible: false,
			oneliner: true,
			hasText: true,
			inlineMenu: [
				{caption: "<i> (italic)", action: Xonomy.wrap, actionParameter: {template: "<i>$</i>", placeholder: "$"}, hideIf: function(jsElement){return false}},
				{caption: "<b> (bold)", action: Xonomy.wrap, actionParameter: {template: "<b>$</b>", placeholder: "$"}, hideIf: function(jsElement){return false}}
			]
		},
		"a": { //an external link
			//backgroundColour: "#d6ffd6",
			attributes: {
				"href": {
					asker: Xonomy.askString,
					askerParameter: null,
					explainer: null,
					menu: [],
					validate: function(jsAttribute) {
						if($.trim(jsAttribute.value)=="") {
							Xonomy.warnings.push({htmlID: jsAttribute.htmlID, text: "The @href attribute should not be empty."});
							return false;
						}
						return true;
					},
				}
			},
			menu: [
				{caption: "Unwrap", action: Xonomy.unwrap, actionParameter: null, hideIf: function(jsElement){return false}}
			],
			canDropTo: [],
			mustBeAfter: [],
			mustBeBefore: [],
			//collapsed: function(jsElement){return true},
			collapsible: true,
			oneliner: true,
			hasText: true,
			inlineMenu: []
		},
	},
	unknownElement: {
		oneliner: true,
		hasText: true,
		menu: [{caption: "Delete", action: Xonomy.deleteElement}],
	},
	unknownAttribute: {
		menu: [{caption: "Delete", action: Xonomy.deleteAttribute}],
	},

};
