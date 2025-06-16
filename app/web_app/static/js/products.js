
function productDetails(product_id){
  return{
    designs:[],

    init(){
      this.fetchDesigns()
    },

    async fetchDesigns() {
      try {
        this.designs = await (await fetch(`/api/v1/product-designs?${product_id}`)).json();
        console.log('Designs: ', this.designs)
      } catch (e) { console.error(e); }
    },

  }
}


function designDetails(design_id){
  return{
    product:null,
    designs:[],

    init(){
      this.fetchVariants()
    },

    async fetchVariants() {
      try {
        this.designs = await (await fetch(`/api/v1/product-variants?${design_id}`)).json();
        console.log('Designs: ', this.designs)
      } catch (e) { console.error(e); }
    },

  }
}