function like(queryId) {
    const likeCount = document.getElementById('likes-count-$(queryId');
    const likeButton = document.getElementById('like-button-$(queryId');
    fetch("/like-blog/${queryId}",{method:"GET"})
        .then((res) => res.json()) 
        .then((data) => {
        likeCount .innerHTML=data['likes'];
        if(data['liked'] == true){
        likeButton.className='fas fa-thumbs-up';
        } else {
            likeButton.className='far fa-thumbs-up';
        } 
        }).catch((e) => alert('could not like post.')) ;   
}