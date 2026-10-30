// Presentation only: the saved answer and its verified source metadata stay intact.
const referencia = /\[F\d+\]/g;
const vazio = node => node.type === 'text' ? !node.value.trim()
 : Array.isArray(node.children) && node.children.every(vazio);

export default function referenciasLegiveis(){
 return tree => {
  function limpar(node){
   if(node.type === 'text'){
    const texto = node.value
     .replace(/Exemplo visual didático criado pela IA, baseado no conceito em (?:\[F\d+\]\s*)+\.?/g,
      'Exemplo visual didático criado pela IA com base nos materiais consultados.')
     .replace(referencia,'');
    const mudou = texto !== node.value;
    node.value = texto;
    return mudou;
   }
   // Code and math nodes have no text children; their literal content is preserved.
   if(!node.children)return false;
   let mudou = false;
   node.children = node.children.filter(child => {
    const alterado = limpar(child);
    mudou ||= alterado;
    return !(alterado && ['paragraph','tableRow','strong','emphasis','link'].includes(child.type) && vazio(child));
   });
   return mudou;
  }
  limpar(tree);
 };
}
