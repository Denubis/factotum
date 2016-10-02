_FactoryFactotum_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _FACTORYFACTOTUM_COMPLETE=complete $1 ) )
    return 0
}

complete -F _FactoryFactotum_completion -o default FactoryFactotum;
