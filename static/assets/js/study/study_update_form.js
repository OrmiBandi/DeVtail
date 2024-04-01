// 태그 추가
document.getElementById('tags-add').addEventListener('click', addTag);

document.getElementById('tags-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        addTag();
        }
    }
);

function addTag() {
    const div_tag = document.createElement('div');
    const tags_container = document.getElementById('tag-container')
    const tag_input = document.getElementById('tags-input');
    const tag_input_value = tag_input.value.trim(); // 입력된 값을 가져와서 공백 제거

    if (!tag_input_value) {
        return; // 입력값이 비어있으면 아무 기능하지 않음
    }
    
    let has_duplicate = false;
    tags_container.querySelectorAll('.tag').forEach(tag => {
        if (tag.textContent === tag_input_value) {
            has_duplicate = true; // 중복된 태그가 있을 경우 true
        }
    });

    if (has_duplicate) {
        return; // 중복된 태그가 있으면 아무 기능하지 않음
    } 

    div_tag.textContent = tag_input_value;
    div_tag.className ='tag hover:cursor-pointer';

    tags_container.appendChild(div_tag);

    // Clear the input field
    tag_input.value = '';
}

// 태그 삭제
document.getElementById('tag-container').addEventListener('click', function(e) {
    if (e.target && e.target.matches('.tag')) {
        e.target.remove();
    }
});

function handleFileSelect(event) {
    const fileInput = event.target;
    const files = fileInput.files;

    // 선택된 파일들을 처리하거나 원하는 동작 수행
    if (files.length > 0) {
        const selectedFile = files[0];

        // FileReader 객체 생성
        const reader = new FileReader();

        // 파일 읽기 완료 시 동작하는 이벤트 리스너
        reader.onload = function (e) {
            const imageData = e.target.result;
    
            // 선택된 이미지를 썸네일 영역에 표시
            document.getElementById('thumbnail-add').src = imageData;
            };
        // 파일을 읽어오기
        reader.readAsDataURL(selectedFile);
    }
}

const link_container = document.querySelector('ref-link-container')

document.getElementById('links_add').addEventListener('click', function(e) {
    const linkContainers = document.querySelectorAll('.ref-link-container');
    e.preventDefault();
    if (linkContainers.length >= 5) {
        document.getElementById('links_add').textContent = '최대 5개까지만 추가할 수 있습니다.'
        document.getElementById('links_add').className = 'btn btn-block'
        return; // 5개 도달시 추가하지 않고 함수 종료
    } else {
        addLinkContainer();
    }
});

function addLinkContainer() {
    const container = document.createElement('div');
    container.className = 'flex gap-4 ref-link-container';
    
    const select = document.createElement('select');
    select.className = 'select select-bordered ref-links-type';
    select.innerHTML = `
        <option value="none select">링크 타입</option>
        <option value="google form">구글 폼</option>
        <option value="book">서적</option>
        <option value="discord">디스코드</option>
        <option value="other">기타</option>
    `;
    
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = '첨부할 url을 입력해주세요.';
    input.className = 'input input-bordered w-full ref_links_url';

    const del_btn = document.createElement('button');
    del_btn.className = 'btn btn-square btn-outline del-btn'
    del_btn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
    `;
    
    container.appendChild(select);
    container.appendChild(input);
    container.appendChild(del_btn);
    
    // 'link-containers'에 새로운 container 추가
    document.getElementById('links-container').appendChild(container)
};

document.getElementById('links-container').addEventListener('click', function(e) {
    if (e.target && e.target.closest('.del-btn')) {
        const toBeRemoved = e.target.closest('.ref-link-container');
        if (toBeRemoved) {
            toBeRemoved.remove();
        }
    }
});

function collectLinks() {
    const links = document.querySelectorAll('#links-container .ref-link-container');
    let links_value = '';
    
    let hasError = false;

    links.forEach((link) => {
        const type = link.querySelector('.ref-links-type').value;
        const url = link.querySelector('.ref_links_url').value;
        if (type === 'none select' && url) {
            hasError = true;
            alert('링크 타입을 선택해주세요.');
        } else if (type !== 'none select' && !url) {
            hasError = true;
            alert('url을 작성해주세요.');
            return;
        } else if (type !== 'none select' && url) {
            links_value += links_value ? ',' + type + ';' + url : type + ';' + url;
        }
    });
    if (hasError) {
        return null;
    } else {
        return links_value;
    }
}

document.getElementById('study_create_form').addEventListener('submit', function(e) {
    e.preventDefault();

    const request_links = document.getElementById('ref_links')
    const collected_links = collectLinks();

    if (collected_links === null) {
        return;
    }
    request_links.value = collected_links;

    const tags = document.getElementById('tags');
    const div_tags_all = document.querySelectorAll('#tag-container div')

    div_tags_all.forEach((div_tag_element) => {
        tags.value += div_tag_element.textContent + ',';
    })
    
    this.submit();
})